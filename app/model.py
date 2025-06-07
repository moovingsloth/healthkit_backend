import pickle
import numpy as np
from typing import Dict, Any, List
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
    
    def predict_concentration(self, health_data: List[Dict[str, Any]]) -> List[float]:
        """
        건강 데이터를 기반으로 집중도를 예측합니다.
        
        Args:
            health_data: 건강 데이터 리스트
            
        Returns:
            예측 결과 리스트
        """
        if not self.model:
            logger.warning("모델이 로드되지 않았습니다. 기본값을 반환합니다.")
            return [0.5 for _ in health_data]
        try:
            features = [
                [
                    d.get('heart_rate', 0),
                    d.get('step_count', 0),
                    d.get('sleep_hours', 0),
                    d.get('stress_level', 0)
                ] for d in health_data
            ]
            return self.model.predict_proba(features)[:, 1].tolist()
        except Exception as e:
            logger.error(f"예측 중 오류 발생: {str(e)}")
            return [0.5 for _ in health_data]
    
    def analyze_focus_pattern(self, health_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        사용자의 집중도 패턴을 분석합니다.
        
        Args:
            health_data: 건강 데이터 리스트
            
        Returns:
            집중도 분석 결과 딕셔너리
        """
        try:
            if not health_data:
                return {
                    "daily_average": 0.0,
                    "weekly_trend": [],
                    "peak_hours": [],
                    "improvement_areas": [],
                    "recommendations": []
                }
            # 일별 평균 집중도 계산
            daily_scores = {}
            for d in health_data:
                date = d.get('date')
                score = d.get('concentration_score', 0.0)
                if date not in daily_scores:
                    daily_scores[date] = []
                daily_scores[date].append(score)
            daily_average = sum([sum(scores)/len(scores) for scores in daily_scores.values()]) / len(daily_scores)
            # 주간 트렌드: float 리스트로 반환
            weekly_trend = [
                sum(scores)/len(scores)
                for date, scores in sorted(daily_scores.items())
            ]
            # 피크 시간대(가장 집중도가 높았던 시간대) 추출
            hour_scores = {}
            for d in health_data:
                hour = d.get('hour')
                score = d.get('concentration_score', 0.0)
                if hour is not None:
                    if hour not in hour_scores:
                        hour_scores[hour] = []
                    hour_scores[hour].append(score)
            if hour_scores:
                peak_hours = sorted(hour_scores.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True)[:3]
                peak_hours = [h for h, _ in peak_hours]
            else:
                peak_hours = []
            # 개선 영역: 문자열 리스트로 반환
            improvement_areas = [
                str(date) for date, scores in daily_scores.items() if (sum(scores)/len(scores)) < 0.5
            ]
            # 추천 생성
            recommendations = self._generate_recommendations(daily_average, health_data)
            return {
                "daily_average": daily_average,
                "weekly_trend": weekly_trend,
                "peak_hours": peak_hours,
                "improvement_areas": improvement_areas,
                "recommendations": recommendations
            }
        except Exception as e:
            logger.error(f"집중 패턴 분석 중 오류 발생: {str(e)}")
            return {
                "daily_average": 0.0,
                "weekly_trend": [],
                "peak_hours": [],
                "improvement_areas": [],
                "recommendations": []
            }
    
    def _generate_recommendations(self, daily_average: float, health_data: List[Dict[str, Any]]) -> List[str]:
        """집중도 점수와 건강 데이터를 기반으로 추천사항을 생성합니다."""
        recs = []
        if daily_average < 0.5:
            recs.append("집중도가 낮습니다. 충분한 수면과 규칙적인 운동을 권장합니다.")
        if any(d.get('sleep_hours', 0) < 6 for d in health_data):
            recs.append("수면 시간이 부족합니다. 6시간 이상 수면을 취하세요.")
        if any(d.get('stress_level', 0) > 7 for d in health_data):
            recs.append("스트레스 지수가 높습니다. 명상이나 휴식을 시도해보세요.")
        if not recs:
            recs.append("집중 패턴이 양호합니다. 현재의 생활 습관을 유지하세요.")
        return recs

# 전역 모델 인스턴스
concentration_model = ConcentrationModel()

def get_concentration_prediction(health_data: List[Dict[str, Any]]) -> List[float]:
    """집중도 예측을 위한 편의 함수"""
    return concentration_model.predict_concentration(health_data) 