import pickle
import numpy as np
from typing import Dict, Any
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConcentrationModel:
    def __init__(self, model_path: str = "model/concentration_model.pkl"):
        """
        집중도 예측 모델 초기화
        
        Args:
            model_path: 모델 파일 경로
        """
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    def load_model(self):
        """사전 학습된 모델을 로드합니다."""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"모델이 성공적으로 로드되었습니다: {self.model_path}")
        except FileNotFoundError:
            logger.warning(f"모델 파일을 찾을 수 없습니다: {self.model_path}")
            logger.info("기본 모델을 사용합니다.")
            self.model = None
        except Exception as e:
            logger.error(f"모델 로드 중 오류 발생: {str(e)}")
            self.model = None
    
    def predict_concentration(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        건강 데이터를 기반으로 집중도를 예측합니다.
        
        Args:
            health_data: 건강 데이터 딕셔너리
            
        Returns:
            예측 결과 딕셔너리
        """
        try:
            if self.model is None:
                # 모델이 없는 경우 기본 예측 로직
                return self._default_prediction(health_data)
            
            # 특성 추출
            features = self._extract_features(health_data)
            
            # 예측 수행
            concentration_score = self.model.predict([features])[0]
            confidence = self.model.predict_proba([features])[0].max()
            
            return {
                "concentration_score": float(concentration_score),
                "confidence": float(confidence),
                "recommendations": self._generate_recommendations(concentration_score, health_data)
            }
            
        except Exception as e:
            logger.error(f"예측 중 오류 발생: {str(e)}")
            return self._default_prediction(health_data)
    
    def _extract_features(self, health_data: Dict[str, Any]) -> list:
        """건강 데이터에서 특성을 추출합니다."""
        features = []
        
        # 심박수 관련 특성
        heart_rate = health_data.get('heart_rate', 70)
        features.append(heart_rate)
        
        # 수면 관련 특성
        sleep_hours = health_data.get('sleep_hours', 7)
        features.append(sleep_hours)
        
        # 활동 관련 특성
        steps = health_data.get('steps', 5000)
        features.append(steps / 1000)  # 정규화
        
        # 스트레스 지수
        stress_level = health_data.get('stress_level', 3)
        features.append(stress_level)
        
        return features
    
    def _default_prediction(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """기본 예측 로직 (모델이 없을 때 사용)"""
        heart_rate = health_data.get('heart_rate', 70)
        sleep_hours = health_data.get('sleep_hours', 7)
        stress_level = health_data.get('stress_level', 3)
        
        # 간단한 휴리스틱 기반 예측
        base_score = 75
        
        # 심박수 조정 (60-80이 이상적)
        if 60 <= heart_rate <= 80:
            heart_rate_adjustment = 10
        elif heart_rate < 60:
            heart_rate_adjustment = -5
        else:
            heart_rate_adjustment = -10
        
        # 수면 시간 조정 (7-9시간이 이상적)
        if 7 <= sleep_hours <= 9:
            sleep_adjustment = 10
        else:
            sleep_adjustment = -5
        
        # 스트레스 조정 (낮을수록 좋음)
        stress_adjustment = -stress_level * 3
        
        concentration_score = max(0, min(100, base_score + heart_rate_adjustment + sleep_adjustment + stress_adjustment))
        
        return {
            "concentration_score": concentration_score,
            "confidence": 0.7,
            "recommendations": self._generate_recommendations(concentration_score, health_data)
        }
    
    def _generate_recommendations(self, score: float, health_data: Dict[str, Any]) -> list:
        """집중도 점수와 건강 데이터를 기반으로 추천사항을 생성합니다."""
        recommendations = []
        
        if score < 50:
            recommendations.append("충분한 휴식을 취하세요.")
            recommendations.append("명상이나 깊은 호흡을 시도해보세요.")
        elif score < 70:
            recommendations.append("가벼운 운동을 통해 활력을 되찾아보세요.")
            recommendations.append("적절한 수분 섭취를 유지하세요.")
        else:
            recommendations.append("현재 좋은 컨디션을 유지하고 있습니다.")
            recommendations.append("이 상태를 지속하기 위해 규칙적인 생활을 유지하세요.")
        
        # 개별 지표 기반 추천
        sleep_hours = health_data.get('sleep_hours', 7)
        if sleep_hours < 6:
            recommendations.append("수면 시간을 늘려보세요 (권장: 7-9시간).")
        
        stress_level = health_data.get('stress_level', 3)
        if stress_level > 7:
            recommendations.append("스트레스 관리가 필요합니다. 요가나 명상을 추천합니다.")
        
        return recommendations

# 전역 모델 인스턴스
concentration_model = ConcentrationModel()

def get_concentration_prediction(health_data: Dict[str, Any]) -> Dict[str, Any]:
    """집중도 예측을 위한 편의 함수"""
    return concentration_model.predict_concentration(health_data) 