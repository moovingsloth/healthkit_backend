import redis.asyncio as aioredis
import json
from datetime import datetime, timedelta
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        self.redis = None
        self.cache_ttl = settings.CACHE_TTL

    async def connect(self):
        """Redis 연결"""
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection error: {str(e)}")
            raise

    async def disconnect(self):
        """Redis 연결 종료"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")

    async def set_health_metrics(self, user_id: str, metrics: dict):
        """건강 데이터 캐싱"""
        try:
            key = f"health_metrics:{user_id}:{metrics['timestamp'].isoformat()}"
            await self.redis.setex(
                key,
                self.cache_ttl,
                json.dumps(metrics)
            )
        except Exception as e:
            logger.error(f"Error caching health metrics: {str(e)}")

    async def get_health_metrics(self, user_id: str, timestamp: datetime):
        """건강 데이터 조회"""
        try:
            key = f"health_metrics:{user_id}:{timestamp.isoformat()}"
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error retrieving health metrics: {str(e)}")
            return None

    async def set_prediction(self, user_id: str, timestamp: datetime, prediction: dict):
        """예측 결과 캐싱"""
        try:
            key = f"prediction:{user_id}:{timestamp.isoformat()}"
            await self.redis.setex(
                key,
                self.cache_ttl,
                json.dumps(prediction)
            )
        except Exception as e:
            logger.error(f"Error caching prediction: {str(e)}")

    async def get_prediction(self, user_id: str, timestamp: datetime):
        """예측 결과 조회"""
        try:
            key = f"prediction:{user_id}:{timestamp.isoformat()}"
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error retrieving prediction: {str(e)}")
            return None

    async def set_user_profile(self, user_id: str, profile: dict):
        """사용자 프로필 캐싱"""
        try:
            key = f"user_profile:{user_id}"
            await self.redis.setex(
                key,
                self.cache_ttl,
                json.dumps(profile)
            )
        except Exception as e:
            logger.error(f"Error caching user profile: {str(e)}")

    async def get_user_profile(self, user_id: str):
        """사용자 프로필 조회"""
        try:
            key = f"user_profile:{user_id}"
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error retrieving user profile: {str(e)}")
            return None

    async def set_focus_analysis(self, user_id: str, start_date: datetime, end_date: datetime, analysis: dict):
        """집중도 분석 결과 캐싱"""
        try:
            key = f"focus_analysis:{user_id}:{start_date.isoformat()}:{end_date.isoformat()}"
            await self.redis.setex(
                key,
                self.cache_ttl,
                json.dumps(analysis)
            )
        except Exception as e:
            logger.error(f"Error caching focus analysis: {str(e)}")

    async def get_focus_analysis(self, user_id: str, start_date: datetime, end_date: datetime):
        """집중도 분석 결과 조회"""
        try:
            key = f"focus_analysis:{user_id}:{start_date.isoformat()}:{end_date.isoformat()}"
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error retrieving focus analysis: {str(e)}")
            return None 