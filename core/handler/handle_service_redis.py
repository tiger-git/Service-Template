
import redis

from config import configure
from utils.util_log import Log


logger = Log()


class RedisHandler(object):
    """
    Redis配置管理
    """

    def __init__(self):
        self.redis_cli = None

    async def init_redis(self):
        """初始化 Redis 连接"""
        self.redis_cli = await redis.asyncio.from_url(configure.redis_url,decode_responses=True)


redis_handler: RedisHandler = RedisHandler()
