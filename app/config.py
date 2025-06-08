import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 기본 설정
    APP_NAME: str = "HealthKit Backend"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # MongoDB 설정
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "healthkit")
    
    # Redis 설정
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # 모델 설정
    MODEL_PATH: str = os.getenv("MODEL_PATH", "model/concentration_model.pkl")
    
    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Google Sheets 설정
    GOOGLE_SHEETS_ID: str = os.getenv("GOOGLE_SHEETS_ID", "")
    
    class Config:
        env_file = ".env"

# 설정 인스턴스 생성
settings = Settings()