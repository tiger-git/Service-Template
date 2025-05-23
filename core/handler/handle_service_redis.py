
import aioredis

from config import configure
from utils.util_log import Log


logger = Log()


class RedisHandler(object):
    """
    Redis配置管理
    """

    def __init__(self):
        self.aioredis = None

    async def init_redis(self):
        """初始化 Redis 连接"""
        self.aioredis = await aioredis.from_url(configure.redis_url)


redis_handler: RedisHandler = RedisHandler()
