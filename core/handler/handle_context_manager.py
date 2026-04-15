import asyncio

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastmcp.server import FastMCP
from fastmcp.server.lifespan import lifespan

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

@lifespan
async def mcp_app_context(app:FastMCP):
    """common context for mcp app, will be called when mcp app start and stop, can be used to init some resource like db connection, redis connection, etc.

    Args:
        app (FastMCP): _description_
    """
    logger.info(f"mcp app context init {app.name}")
    # await redis_handler.init_redis()
    logger.info(f"mcp app context init finished {app.name}")
    yield
    logger.warning(f"mcp app context stop ing... {app.name}")
    logger.warning(f"mcp app context stop finished {app.name}")