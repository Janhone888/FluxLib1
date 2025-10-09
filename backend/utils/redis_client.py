# utils/redis_client.py
import redis
import json
import os
from config import logger


class RedisClient:
    def __init__(self):
        try:
            self.client = redis.Redis(
                host=os.getenv('REDIS_HOST'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                password=os.getenv('REDIS_PASSWORD'),
                db=int(os.getenv('REDIS_DB', 0)),
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=3
            )
            # 测试连接
            self.client.ping()
            logger.info("✅ Redis连接成功")
        except Exception as e:
            logger.error(f"❌ Redis连接失败: {e}")
            self.client = None

    def get_user(self, user_id):
        """获取用户缓存"""
        if not self.client:
            return None
        try:
            data = self.client.get(f"user:{user_id}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis获取用户失败: {e}")
            return None

    def set_user(self, user_id, user_data, expire=3600):
        """设置用户缓存"""
        if not self.client:
            return
        try:
            self.client.setex(
                f"user:{user_id}",
                expire,
                json.dumps(user_data)
            )
        except Exception as e:
            logger.error(f"Redis设置用户失败: {e}")

    def get_user_by_token(self, token):
        """通过token获取用户ID"""
        if not self.client:
            return None
        try:
            return self.client.get(f"token:{token}")
        except Exception as e:
            logger.error(f"Redis获取token失败: {e}")
            return None

    def set_token_user(self, token, user_id, expire=7200):
        """设置token-用户映射"""
        if not self.client:
            return
        try:
            self.client.setex(f"token:{token}", expire, user_id)
        except Exception as e:
            logger.error(f"Redis设置token失败: {e}")


# 全局Redis客户端
redis_client = RedisClient()