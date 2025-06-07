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
    """루트 엔드포인트 - API 상태 확인"""
    return {
        "message": "HealthKit 집중도 예측 API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/predict/concentration", response_model=ConcentrationPrediction)
async def predict_concentration(
    metrics: HealthMetrics,
    background_tasks: BackgroundTasks
):
    """
    건강 데이터를 기반으로 집중도를 예측합니다.
    
    Args:
        metrics: 건강 데이터 입력
        
    Returns:
        집중도 예측 결과
    """
    try:
        # 캐시에서 예측 결과 확인
        cached_prediction = await cache_service.get_prediction(
            metrics.user_id,
            metrics.date
        )
        if cached_prediction:
            return cached_prediction
            
        # 모델로 예측
        prediction = model.predict_concentration(metrics.dict())
        
        # 캐시에 저장
        await cache_service.set_prediction(
            metrics.user_id,
            metrics.date,
            prediction
        )
        
        logger.info(f"집중도 예측 완료: {prediction['concentration_score']:.1f}")
        return prediction
        
    except Exception as e:
        logger.error(f"집중도 예측 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"예측 처리 중 오류가 발생했습니다: {str(e)}")

@app.post("/api/health-metrics", response_model=HealthMetrics)
async def store_health_metrics(
    metrics: HealthMetrics,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    try:
        # 데이터베이스에 저장
        await db.health_metrics.insert_one(metrics.dict())
        
        # 캐시 업데이트
        await cache_service.set_health_metrics(metrics.user_id, metrics)
        
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health-metrics/{user_id}")
async def get_recent_metrics(user_id: str):
    if user_id not in health_data_store:
        return {"data": []}
    
    # 최근 30분 데이터 반환
    current_time = datetime.now()
    recent_data = [
        data for data in health_data_store[user_id]
        if current_time - data.timestamp < timedelta(minutes=30)
    ]
    
    return {"data": recent_data}

@app.get("/api/user/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(user_id: str, db = Depends(get_db)):
    """
    사용자 프로필을 조회합니다.
    
    Args:
        user_id: 사용자 ID
        
    Returns:
        사용자 프로필 정보
    """
    try:
        # 캐시에서 먼저 확인
        cached_profile = await cache_service.get_user_profile(user_id)
        if cached_profile:
            return cached_profile
            
        # 데이터베이스에서 조회
        profile = await db.user_profiles.find_one({"user_id": user_id})
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
            
        # 캐시에 저장
        await cache_service.set_user_profile(user_id, profile)
        
        logger.info(f"사용자 프로필 조회: {user_id}")
        return profile
        
    except Exception as e:
        logger.error(f"사용자 프로필 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{user_id}/concentration-analysis", response_model=FocusAnalysis)
def get_concentration_analysis(user_id: str):
    """
    사용자의 집중도 분석 결과를 조회합니다.
    
    Args:
        user_id: 사용자 ID
        
    Returns:
        집중도 분석 결과
    """
    try:
        # 실제 구현에서는 데이터베이스에서 분석 데이터 조회
        # 현재는 더미 데이터 반환
        analysis = FocusAnalysis(
            daily_average=75.2,
            weekly_trend=[72.1, 74.5, 78.2, 76.8, 75.9, 77.3, 75.2],
            peak_hours=[9, 10, 14, 15],
            improvement_areas=["수면 품질", "스트레스 관리"]
        )
        
        logger.info(f"집중도 분석 조회: {user_id}")
        return analysis
        
    except Exception as e:
        logger.error(f"집중도 분석 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="집중도 분석 조회 중 오류가 발생했습니다.")

@app.get("/api/user/{user_id}/focus-pattern", response_model=FocusAnalysis)
async def get_user_focus_pattern(
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db = Depends(get_db)
):
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()
            
        # 캐시에서 분석 결과 확인
        cached_analysis = await cache_service.get_focus_analysis(
            user_id,
            start_date,
            end_date
        )
        if cached_analysis:
            return cached_analysis
            
        # 데이터베이스에서 데이터 조회
        metrics = await db.health_metrics.find({
            "user_id": user_id,
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }).to_list(length=None)
        
        if not metrics:
            raise HTTPException(status_code=404, detail="No data found for the specified period")
            
        # 분석 수행
        analysis = model.analyze_focus_pattern(metrics)
        
        # 캐시에 저장
        await cache_service.set_focus_analysis(
            user_id,
            start_date,
            end_date,
            analysis
        )
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket 연결을 처리하는 엔드포인트"""
    try:
        await manager.connect(websocket, user_id)
        logger.info(f"WebSocket connection established for user {user_id}")
        
        while True:
            try:
                data = await websocket.receive_json()
                logger.info(f"Received data from user {user_id}: {data}")
                
                # 클라이언트로부터 받은 데이터 처리
                if data.get("type") == "health_update":
                    await manager.broadcast_health_update(user_id, data.get("data", {}))
                elif data.get("type") == "concentration_update":
                    await manager.broadcast_concentration_update(user_id, data.get("data", {}))
                    
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for user {user_id}")
                manager.disconnect(websocket, user_id)
                break
            except Exception as e:
                logger.error(f"WebSocket error for user {user_id}: {str(e)}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        manager.disconnect(websocket, user_id)

# 개발용 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)