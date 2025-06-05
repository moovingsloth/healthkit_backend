from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging
from typing import Optional
from .config import settings

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect_to_database(cls):
        """MongoDB 데이터베이스에 연결"""
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            
            # 연결 테스트
            await cls.client.admin.command('ping')
            logger.info("MongoDB 연결 성공")
            
            # 인덱스 생성
            await cls.create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB 연결 실패: {str(e)}")
            raise

    @classmethod
    async def create_indexes(cls):
        """컬렉션 인덱스 생성"""
        try:
            # health_metrics 컬렉션 인덱스
            await cls.db.health_metrics.create_index([
                ("user_id", 1),
                ("timestamp", -1)
            ])
            
            # user_profiles 컬렉션 인덱스
            await cls.db.user_profiles.create_index([
                ("user_id", 1)
            ], unique=True)
            
            # predictions 컬렉션 인덱스
            await cls.db.predictions.create_index([
                ("user_id", 1),
                ("timestamp", -1)
            ])
            
            logger.info("데이터베이스 인덱스 생성 완료")
            
        except Exception as e:
            logger.error(f"인덱스 생성 중 오류 발생: {str(e)}")
            raise

    @classmethod
    async def close_database_connection(cls):
        """데이터베이스 연결 종료"""
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("MongoDB 연결 종료")

    @classmethod
    async def get_db(cls):
        """데이터베이스 인스턴스를 반환합니다."""
        if cls.db is None:
            await cls.connect_to_database()
        return cls.db

async def init_db():
    """데이터베이스 초기화"""
    await Database.connect_to_database()
    
    # 인덱스 생성
    db = await Database.get_db()
    
    # health_metrics 컬렉션 인덱스
    await db.health_metrics.create_index([
        ("user_id", 1),
        ("timestamp", -1)
    ])
    
    # user_profiles 컬렉션 인덱스
    await db.user_profiles.create_index([
        ("user_id", 1)
    ], unique=True)
    
    logger.info("Database indexes created")

async def get_db():
    """데이터베이스 의존성 주입"""
    return await Database.get_db() 