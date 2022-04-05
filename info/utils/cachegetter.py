import redis
from config import DevelopmentConfig


def verify_code_cache():
    return redis.Redis(**DevelopmentConfig.VERIFY_CODE_CACHE)