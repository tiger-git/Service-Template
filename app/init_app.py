import datetime

from sqlalchemy import select

from fastapi import FastAPI, Request,Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, HTMLResponse

from core.handler.handle_context_manager import context
from core.services.handle_service import ServiceError, error_response
from core.services.handle_service_redis import redis_handler
from models.base import SessionDep
from core.items.enum_system import ErrorCodeEnum
from utils.util_log import Log


logger = Log()

app = FastAPI(
    lifespan=context,
    version="1.0.0",
    description="Web Service Template",
)
app.mount("/static", StaticFiles(directory="static"))
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["signature"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常捕获
    :param request:
    :param exc:
    :return:
    """
    logger.error(f"UnKnown Exception occurred: {exc} in API {request.url.path}")
    return JSONResponse(
        status_code=exec.status_code if hasattr(exc, "status_code") else 500,
        content=error_response(ErrorCodeEnum.SystemError, f"error:{exc}").model_dump(
            mode="json"
        ),
    )


@app.exception_handler(ServiceError)
async def common_exception(request: Request, e: ServiceError):
    """
    自定义异常捕获
    :param request:
    :param e:
    :return:
    """
    content = error_response(e.code, e.message, e.error_msg).model_dump(mode="json")
    # 需要重点监测的错误【系统优化】
    if e.code in (ErrorCodeEnum.SystemError, ErrorCodeEnum.SDKMysqlError):
        logger.error(
            f"Known Exception occurred:{e.code} {e.error_msg} in API {request.url.path}"
        )
        return JSONResponse(status_code=500, content=content)
    # 后期可根据需要，再细分status code,如超时，客户端输入错误等
    logger.info(f"Known Exception:{e.message} {e.error_msg} in API {request.url.path}")
    return JSONResponse(content=content)
