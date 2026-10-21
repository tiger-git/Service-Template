from fastapi import APIRouter
from .controller.controller_user import router as demo_router
from .controller.controller_role_acl import router as role_acl_router

routers = APIRouter()
routers.include_router(demo_router, tags=["User"], prefix="/api/v1")
routers.include_router(role_acl_router, tags=["Role"], prefix="/backend/v1")
