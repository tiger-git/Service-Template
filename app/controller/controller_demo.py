import datetime
from fastapi import APIRouter

from core.handler.handle_service import success_response
from core.items.item_request import ItemUserRegisterRequest
from core.items.item_response import ItemUserRegisterResponse, ItemUserRegisterResult
from models.base import SessionDep
from models.model_demo import User
from utils.util_log import Log

logger = Log()

router = APIRouter()


@router.post("/user", response_model=ItemUserRegisterResponse)
async def user(param: ItemUserRegisterRequest, session: SessionDep):
    key_hash = str(int(datetime.datetime.now().timestamp()))
    session.add(User(key_hash=key_hash, **param.model_dump(mode='json')))
    await session.commit()
    return success_response(data=ItemUserRegisterResult(user_id=key_hash))
