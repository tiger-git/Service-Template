from fastapi import APIRouter
from .controller.controller_demo import router as demo_router
from .controller.controller_mcp_tools import router as mcp_tools_router

routers = APIRouter()
routers.include_router(demo_router, tags=["Demo"])
routers.include_router(mcp_tools_router, tags=["MCP"])
