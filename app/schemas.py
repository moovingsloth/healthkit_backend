from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class HealthDataInput(BaseModel):
    """건강 데이터 입력 스키마"""
    heart_rate: Optional[int] = Field(default=70, ge=40, le=200, description="심박수 (BPM)")
    sleep_hours: Optional[float] = Field(default=7.0, ge=0, le=24, description="수면 시간 (시간)")
    steps: Optional[int] = Field(default=5000, ge=0, description="걸음 수")
    stress_level: Optional[int] = Field(default=3, ge=1, le=10, description="스트레스 지수 (1-10)")
    activity_level: Optional[int] = Field(default=3, ge=1, le=10, description="활동 강도 (1-10)")
    caffeine_intake: Optional[int] = Field(default=1, ge=0, le=10, description="카페인 섭취량 (잔)")
    water_intake: Optional[float] = Field(default=2.0, ge=0, description="수분 섭취량 (리터)")
    
    class Config:
        schema_extra = {
            "example": {
                "heart_rate": 75,
                "sleep_hours": 7.5,
                "steps": 8000,
                "stress_level": 4,
                "activity_level": 6,
                "caffeine_intake": 2,
                "water_intake": 2.5
            }
        }

class ConcentrationPrediction(BaseModel):
    """집중도 예측 결과 스키마"""
    concentration_score: float = Field(description="집중도 점수 (0-100)")
    confidence: float = Field(description="예측 신뢰도 (0-1)")
    recommendations: List[str] = Field(description="개선 추천사항 목록")
    timestamp: datetime = Field(default_factory=datetime.now, description="예측 시간")
    
    class Config:
        schema_extra = {
            "example": {
                "concentration_score": 78.5,
                "confidence": 0.85,
                "recommendations": [
                    "현재 좋은 컨디션을 유지하고 있습니다.",
                    "이 상태를 지속하기 위해 규칙적인 생활을 유지하세요."
                ],
                "timestamp": "2024-01-15T10:30:00"
            }
        }

class HealthMetrics(BaseModel):
    """건강 지표 조회 결과 스키마"""
    user_id: str = Field(description="사용자 ID")
    date: datetime = Field(description="측정 날짜")
    heart_rate_avg: Optional[float] = Field(description="평균 심박수")
    heart_rate_resting: Optional[float] = Field(description="안정시 심박수")
    sleep_duration: Optional[float] = Field(description="수면 시간")
    sleep_quality: Optional[float] = Field(description="수면 품질 점수")
    steps_count: Optional[int] = Field(description="걸음 수")
    active_calories: Optional[float] = Field(description="활동 칼로리")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "date": "2024-01-15T00:00:00",
                "heart_rate_avg": 72.5,
                "heart_rate_resting": 60.0,
                "sleep_duration": 7.5,
                "sleep_quality": 8.2,
                "steps_count": 9500,
                "active_calories": 450.2
            }
        }

class UserProfile(BaseModel):
    """사용자 프로필 스키마"""
    user_id: str = Field(description="사용자 ID")
    name: str = Field(description="사용자 이름")
    age: Optional[int] = Field(default=None, ge=1, le=150, description="나이")
    gender: Optional[str] = Field(default=None, description="성별")
    height: Optional[float] = Field(default=None, ge=50, le=300, description="신장 (cm)")
    weight: Optional[float] = Field(default=None, ge=20, le=500, description="체중 (kg)")
    activity_goal: Optional[int] = Field(default=10000, description="일일 걸음 목표")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "name": "홍길동",
                "age": 30,
                "gender": "male",
                "height": 175.0,
                "weight": 70.0,
                "activity_goal": 10000
            }
        }

class APIResponse(BaseModel):
    """API 응답 기본 스키마"""
    success: bool = Field(description="요청 성공 여부")
    message: str = Field(description="응답 메시지")
    data: Optional[dict] = Field(default=None, description="응답 데이터")
    error: Optional[str] = Field(default=None, description="에러 메시지")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "요청이 성공적으로 처리되었습니다.",
                "data": {},
                "error": None
            }
        }

class FocusAnalysis(BaseModel):
    """집중도 분석 결과 스키마"""
    daily_average: float = Field(description="일일 평균 집중도")
    weekly_trend: List[float] = Field(description="주간 트렌드")
    peak_hours: List[int] = Field(description="집중도가 높은 시간대")
    improvement_areas: List[str] = Field(description="개선이 필요한 영역")
    
    class Config:
        schema_extra = {
            "example": {
                "daily_average": 75.2,
                "weekly_trend": [72.1, 74.5, 78.2, 76.8, 75.9, 77.3, 75.2],
                "peak_hours": [9, 10, 14, 15],
                "improvement_areas": ["수면 품질", "스트레스 관리"]
            }
        } 
        
# 한 센서 시계열 (ex: bpm, temp 등)
class TimeSeriesItem(BaseModel):
    timestamp: datetime
    value: float

# 전체 입력: 시계열 + 현재 시간
class RealTimeFeatureInput(BaseModel):
    pid: str
    current_time: datetime
    bpm: List[TimeSeriesItem]
    temp: List[TimeSeriesItem]
    light: List[TimeSeriesItem]
    interval: List[TimeSeriesItem]