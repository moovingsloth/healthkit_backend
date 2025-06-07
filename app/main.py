from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from .model import get_concentration_prediction, ConcentrationModel
from .schemas import (
    HealthDataInput,
    ConcentrationPrediction,
    APIResponse,
    HealthMetrics,
    UserProfile,
    FocusAnalysis
)
from .database import get_db, init_db, Database
from .services.cache_service import RedisCache
from .config import settings
from .websocket import manager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="HealthKit Backend API",
    description="건강 데이터를 기반으로 집중도를 예측하는 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 초기화
cache_service = RedisCache()
model = ConcentrationModel()

async def init_redis():
    """Redis 연결 초기화"""
    await cache_service.connect()
    logger.info("Redis connection established")

async def close_redis():
    """Redis 연결 종료"""
    await cache_service.disconnect()
    logger.info("Redis connection closed")

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행되는 이벤트 핸들러"""
    await init_db()
    await init_redis()

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 실행되는 이벤트 핸들러"""
    await Database.close_database_connection()
    await close_redis()

@app.get("/")
def read_root():
    logger.info("[root] 요청 수신")
    result = {
        "message": "HealthKit 집중도 예측 API",
        "version": "1.0.0",
        "status": "running"
    }
    logger.info(f"[root] 응답: {result}")
    return result

@app.get("/health")
async def health_check():
    logger.info("[health] 요청 수신")
    result = {"status": "healthy", "timestamp": datetime.now()}
    logger.info(f"[health] 응답: {result}")
    return result

@app.post("/predict/concentration", response_model=ConcentrationPrediction)
async def predict_concentration(
    metrics: HealthMetrics,
    background_tasks: BackgroundTasks
):
    logger.info(f"[predict/concentration] 요청: {metrics}")
    try:
        cached_prediction = await cache_service.get_prediction(
            metrics.user_id,
            metrics.date
        )
        if cached_prediction:
            logger.info(f"[predict/concentration] 캐시 HIT: {cached_prediction}")
            return cached_prediction
        prediction = model.predict_concentration(metrics.dict())
        await cache_service.set_prediction(
            metrics.user_id,
            metrics.date,
            prediction
        )
        logger.info(f"[predict/concentration] 예측 결과: {prediction}")
        return prediction
    except Exception as e:
        logger.error(f"[predict/concentration] 에러: {str(e)} | 요청: {metrics}")
        raise HTTPException(status_code=500, detail=f"예측 처리 중 오류가 발생했습니다: {str(e)}")

@app.post("/api/health-metrics", response_model=HealthMetrics)
async def store_health_metrics(
    metrics: HealthMetrics,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    logger.info(f"[store_health_metrics] 요청: {metrics}")
    try:
        await db.health_metrics.insert_one(metrics.dict())
        await cache_service.set_health_metrics(metrics.user_id, metrics)
        logger.info(f"[store_health_metrics] 저장 완료: {metrics.user_id}")
        return metrics
    except Exception as e:
        logger.error(f"[store_health_metrics] 에러: {str(e)} | 요청: {metrics}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health-metrics/{user_id}")
async def get_recent_metrics(user_id: str):
    logger.info(f"[get_recent_metrics] 요청: user_id={user_id}")
    if user_id not in health_data_store:
        logger.info(f"[get_recent_metrics] 데이터 없음: user_id={user_id}")
        return {"data": []}
    current_time = datetime.now()
    recent_data = [
        data for data in health_data_store[user_id]
        if current_time - data.timestamp < timedelta(minutes=30)
    ]
    logger.info(f"[get_recent_metrics] 반환 데이터 개수: {len(recent_data)}")
    return {"data": recent_data}

@app.get("/api/user/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(user_id: str, db = Depends(get_db)):
    logger.info(f"[get_user_profile] 요청: user_id={user_id}")
    try:
        cached_profile = await cache_service.get_user_profile(user_id)
        if cached_profile:
            logger.info(f"[get_user_profile] 캐시 HIT: user_id={user_id}")
            return cached_profile
        profile = await db.user_profiles.find_one({"user_id": user_id})
        if not profile:
            logger.warning(f"[get_user_profile] 프로필 없음: user_id={user_id}")
            raise HTTPException(status_code=404, detail="User profile not found")
        await cache_service.set_user_profile(user_id, profile)
        logger.info(f"[get_user_profile] DB 조회 및 캐시 저장: user_id={user_id}")
        return profile
    except Exception as e:
        logger.error(f"[get_user_profile] 에러: {str(e)} | user_id={user_id}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{user_id}/concentration-analysis", response_model=FocusAnalysis)
def get_concentration_analysis(user_id: str):
    logger.info(f"[get_concentration_analysis] 요청: user_id={user_id}")
    try:
        analysis = FocusAnalysis(
            daily_average=75.2,
            weekly_trend=[72.1, 74.5, 78.2, 76.8, 75.9, 77.3, 75.2],
            peak_hours=[9, 10, 14, 15],
            improvement_areas=["수면 품질", "스트레스 관리"]
        )
        logger.info(f"[get_concentration_analysis] 더미 데이터 반환: user_id={user_id}")
        return analysis
    except Exception as e:
        logger.error(f"[get_concentration_analysis] 에러: {str(e)} | user_id={user_id}")
        raise HTTPException(status_code=500, detail="집중도 분석 조회 중 오류가 발생했습니다.")

@app.get("/api/user/{user_id}/focus-pattern", response_model=FocusAnalysis)
async def get_user_focus_pattern(
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db = Depends(get_db)
):
    logger.info(f"[focus-pattern] 요청: user_id={user_id}, start_date={start_date}, end_date={end_date}")
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()
        logger.info(f"[focus-pattern] 쿼리 범위: start_date={start_date}, end_date={end_date}")
        cached_analysis = await cache_service.get_focus_analysis(user_id, start_date, end_date)
        if cached_analysis:
            logger.info(f"[focus-pattern] 캐시 HIT: user_id={user_id}")
            return cached_analysis
        metrics = await db.health_metrics.find({
            "user_id": user_id,
            "date": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=None)
        logger.info(f"[focus-pattern] DB 조회: user_id={user_id}, metrics_count={len(metrics)}")
        if not metrics:
            logger.warning(f"[focus-pattern] 데이터 없음: user_id={user_id}")
            raise HTTPException(status_code=404, detail="No data found for the specified period")
        analysis = model.analyze_focus_pattern(metrics)
        logger.info(f"[focus-pattern] 분석 결과: user_id={user_id}, daily_avg={analysis.get('daily_average')}")
        await cache_service.set_focus_analysis(user_id, start_date, end_date, analysis)
        logger.info(f"[focus-pattern] 캐시 저장: user_id={user_id}")
        return analysis
    except Exception as e:
        logger.error(f"[focus-pattern] 에러: user_id={user_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    logger.info(f"[websocket] 연결 요청: user_id={user_id}")
    try:
        await manager.connect(websocket, user_id)
        logger.info(f"[websocket] 연결 완료: user_id={user_id}")
        while True:
            try:
                data = await websocket.receive_json()
                logger.info(f"[websocket] 데이터 수신: user_id={user_id}, data={data}")
                if data.get("type") == "health_update":
                    await manager.broadcast_health_update(user_id, data.get("data", {}))
                elif data.get("type") == "concentration_update":
                    await manager.broadcast_concentration_update(user_id, data.get("data", {}))
            except WebSocketDisconnect:
                logger.info(f"[websocket] 연결 해제: user_id={user_id}")
                manager.disconnect(websocket, user_id)
                break
            except Exception as e:
                logger.error(f"[websocket] 내부 에러: user_id={user_id}, error={str(e)}")
                break
    except Exception as e:
        logger.error(f"[websocket] 연결 에러: user_id={user_id}, error={str(e)}")
        manager.disconnect(websocket, user_id)

# 개발용 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)