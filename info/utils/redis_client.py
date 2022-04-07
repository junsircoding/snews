"""
Redis 客户端
"""
import redis
from config import DevelopmentConfig


def redis_client():
    """Redis 客户端"""
    return redis.Redis(**DevelopmentConfig.VERIFY_CODE_CACHE)