from fastapi import APIRouter
from .controller.controller_user import router as demo_router

routers = APIRouter()
routers.include_router(demo_router, tags=["User"], prefix="/api/v1")
