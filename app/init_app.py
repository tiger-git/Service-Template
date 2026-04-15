import datetime

from sqlalchemy import select

from fastapi import FastAPI, Request,Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, HTMLResponse
from fastmcp.utilities.lifespan import combine_lifespans

from core.handler.handle_context_manager import context
from core.handler.handle_service import ServiceError, error_response
from core.handler.handle_service_redis import redis_handler
from models.model_demo import IpInfo
from models.base import SessionDep
from core.items.enum_system import ErrorCodeEnum
from utils.util_log import Log

from .init_mcp import mcp_echo_app, mcp_weather_app


logger = Log()

app = FastAPI(
    lifespan=combine_lifespans(context, mcp_echo_app.lifespan, mcp_weather_app.lifespan),
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
        status_code=500,
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


@app.get("/", response_class=HTMLResponse,tags=["Demo"])
async def index(request: Request,db:SessionDep):
    """index page

    Args:
        request (Request): _description_
        db (SessionDep): _description_

    Returns:
        _type_: _description_
    """
    current_time = await redis_handler.redis_cli.get("current_time")
    if not current_time:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await redis_handler.redis_cli.set("current_time", current_time, 60)
    ip_address = request.client.host
    ip_info = await db.execute(select(IpInfo).where(IpInfo.ip_address==ip_address))
    if row:= ip_info.scalar_one_or_none():
        row.updated_time = datetime.datetime.now()
    else:
        row = IpInfo(ip_address=ip_address)
        db.add(row)
    await db.commit()
    await db.refresh(row)
    rows = await db.execute(select(IpInfo).order_by(IpInfo.created_time))
    data = rows.scalars().all()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"current_time": current_time,"records":data},
    )
