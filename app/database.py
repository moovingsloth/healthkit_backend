from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect_to_database(cls):
        """MongoDB 연결 설정"""
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            # 설정이 없을 경우 기본값 사용
            db_name = getattr(settings, 'MONGODB_DB_NAME', 'healthkit_db')
            cls.db = cls.client[db_name]
            logger.info("MongoDB 연결 성공")
            return cls.db
        except Exception as e:
            logger.error(f"MongoDB 연결 오류: {str(e)}")
            # 개발 환경에서는 연결 실패해도 계속 진행
            if os.environ.get('ENV') == 'development':
                logger.warning("개발 환경: MongoDB 모의 객체 사용")
                return MockDatabase()
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

class MockDatabase:
    """개발 환경에서 사용할 모의 데이터베이스"""
    def __init__(self):
        self.collections = {}
        self.health_metrics = []
        self.users = []
        logger.info("모의 데이터베이스 초기화됨")
    
    async def get_collection(self, name):
        if name not in self.collections:
            self.collections[name] = MockCollection(name)
        return self.collections[name]

class MockCollection:
    """모의 컬렉션 클래스"""
    def __init__(self, name):
        self.name = name
        self.data = []
    
    async def insert_one(self, document):
        document['_id'] = len(self.data) + 1
        self.data.append(document)
        return document
    
    async def find(self, query=None):
        # 간단한 필터링 로직
        return self.data
    
    # 기타 필요한 메서드들...