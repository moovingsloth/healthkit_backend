import os
import pickle
import numpy as np
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional

# 외부 라이브러리 임포트 (예외 처리)
try:
    import joblib
    from sklearn.ensemble import RandomForestClassifier
except ImportError:
    joblib = None

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 여기서 순환 참조를 제거: .model에서 자기 자신을 import하지 않도록 수정
# from .model import get_concentration_prediction, ConcentrationModel <- 이 라인 삭제

class ConcentrationModel:
    def __init__(self):
        self.model = self._load_model()
        
    def _load_model(self):
        try:
            # 모델 파일 로드 시도
            model_path = "model/concentration_model.pkl"  # 하드코딩하거나 settings에서 가져옴
            if os.path.exists(model_path):
                return joblib.load(model_path)
            else:
                logger.warning(f"모델 파일을 찾을 수 없습니다: {model_path}. 기본 예측 사용.")
                return None
        except Exception as e:
            logger.error(f"모델 로드 중 오류 발생: {str(e)}")
            return None
    
    def predict_concentration(self, data):
        try:
            logger.debug(f"predict_concentration 호출: {type(data).__name__} 데이터")
            
            # Pydantic 모델을 딕셔너리로 변환
            if hasattr(data, 'dict'):
                data = data.dict()
            elif isinstance(data, str):
                try:
                    # 문자열인 경우 JSON으로 파싱 시도
                    import json
                    data = json.loads(data)
                except Exception as e:
                    logger.error(f"문자열을 JSON으로 파싱할 수 없습니다: {data[:100]}, 오류: {str(e)}")
                    return self._return_default_prediction()
            
            # 예측에 필요한 필드 확인
            required_fields = [
                "heart_rate_avg", "heart_rate_resting", "sleep_duration", 
                "sleep_quality", "steps_count", "active_calories"
            ]
            
            # 모든 필드가 있는지 확인하고 없으면 기본값 설정
            for field in required_fields:
                if not isinstance(data, dict) or field not in data or data[field] is None:
                    if isinstance(data, dict):
                        logger.warning(f"누락된 필드: {field}. 기본값 사용.")
                        data[field] = 0  # 기본값 설정
                    else:
                        logger.error(f"데이터가 딕셔너리 형태가 아닙니다: {type(data)}")
                        return self._return_default_prediction()
            
            # 기본값으로 휴리스틱 예측 사용
            return self._heuristic_prediction(data)
                
        except Exception as e:
            logger.error(f"예측 처리 중 오류: {str(e)}")
            logger.error(f"상세 오류 정보:\n{traceback.format_exc()}")
            # 오류 발생 시 기본값 반환
            return self._return_default_prediction()
    
    def _return_default_prediction(self):
        """기본 예측값 반환"""
        return {
            "concentration_score": 65.0,
            "confidence": 0.7,
            "recommendations": ["기본 추천사항입니다."],
            "timestamp": datetime.now().isoformat()
        }
    
    def _heuristic_prediction(self, data):
        """간단한 휴리스틱으로 집중도 예측"""
        try:
            # 심박수 기여도 (낮은 심박수 = 높은 집중도)
            heart_rate_score = 100 - (float(data.get("heart_rate_avg", 75)) - 60) * 1.5
            if heart_rate_score < 0: heart_rate_score = 0
            if heart_rate_score > 100: heart_rate_score = 100
            
            # 수면 기여도 (적정 수면 = 높은 집중도)
            sleep_score = float(data.get("sleep_quality", 5)) * 10
            if sleep_score > 100: sleep_score = 100
            
            # 활동량 기여도
            activity_score = min(float(data.get("steps_count", 5000)) / 100, 100)
            
            # 가중 평균으로 최종 점수 계산
            final_score = (heart_rate_score * 0.4 + sleep_score * 0.4 + activity_score * 0.2)
            
            # 딕셔너리 반환
            return {
                "concentration_score": float(final_score),
                "confidence": 0.8,
                "recommendations": [
                    "현재 상태를 기반으로 한 추천사항입니다.",
                    "규칙적인 수면 패턴을 유지하세요."
                ],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"휴리스틱 예측 중 오류: {str(e)}")
            logger.error(f"상세 오류 정보:\n{traceback.format_exc()}")
            return self._return_default_prediction()

# 전역 모델 인스턴스
concentration_model = None

def initialize_model():
    """모델 초기화 함수"""
    global concentration_model
    logger.info("ConcentrationModel 초기화 중...")
    concentration_model = ConcentrationModel()
    logger.info("ConcentrationModel 초기화 완료")

def get_concentration_prediction(health_data):
    """집중도 예측을 위한 편의 함수"""
    global concentration_model
    if concentration_model is None:
        initialize_model()
    return concentration_model.predict_concentration(health_data)