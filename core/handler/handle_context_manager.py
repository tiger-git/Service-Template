import asyncio

from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.handler import redis_handler
from models.base import Base,engine
from utils.util_log import Log


logger = Log()


@asynccontextmanager
async def context(app: FastAPI):
    """
    项目启动时预加载信息
    :param app:
    :return:
    """
    logger.info("ready start app, init ...")
    await redis_handler.init_redis()
    # 创建表
    async with engine.begin() as db:
        await db.run_sync(Base().metadata.create_all)
    loop = asyncio.get_event_loop()
    logger.info("init app finished")
    yield
    logger.warning("stop app ing...")
    logger.warning("stop app finished")
