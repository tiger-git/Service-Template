from fastapi import APIRouter
from .controller.controller_demo import router as demo_router

routers = APIRouter()
routers.include_router(demo_router, tags=["Demo"])
