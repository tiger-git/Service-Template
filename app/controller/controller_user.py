from fastapi import APIRouter, HTTPException,Request
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from core.items.enum_system import ErrorCodeEnum
from core.items.item_base import ItemRefreshToken
from core.services.handle_service import success_response,error_response
from core.items.item_request import ItemUserRegisterRequest
from core.items.item_response import ItemUserInfoResponse, ItemUserInfoResult, ItemUserRegisterResponse, ItemUserRegisterResult, ItemUserLoginResult
from models.base import SessionDep
from models.user import User
from utils.util_log import Log
from utils.util_object import get_uuid,generate_random_hex
from core.handler.handler_user import check_password, generate_token_hash, get_current_user, hash_password,create_access_token,create_refresh_token, verify_refresh_token
from core.services.handle_service_redis import redis_handler
from core.items.constant import REDIS_KEY_REFRESH_TOKENS
logger = Log()

router = APIRouter()


@router.post("/user/register", response_model=ItemUserRegisterResponse)
async def register(param: ItemUserRegisterRequest, session: SessionDep):
    key_hash = get_uuid()
    user_exists = await session.scalar(select(User).filter(User.email == param.email))
    if user_exists:
        return error_response(ErrorCodeEnum.InputParamsError, error_msg="Email already exists")
    # check and update key_hash for security
    if await session.scalar(select(User).filter(User.key_hash == key_hash)):
        key_hash = get_uuid()
        logger.info(f"Generated new key_hash: {key_hash} for user registration due to collision.")
    salt = generate_random_hex()
    password_hash = hash_password(param.password, salt)
    if not param.nick_name:
        param.nick_name = f"{param.email.split('@')[0]}-{key_hash[:5]}"
    session.add(User(key_hash=key_hash, nick_name=param.nick_name, email=param.email, password_hash=password_hash, salt=salt))
    await session.commit()
    return success_response(data=ItemUserRegisterResult(user_id=key_hash))


@router.post("/user/login", response_model=ItemUserLoginResult)
async def login(session: SessionDep,request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await session.scalar(select(User).filter(User.email == form_data.username))
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect password or email")
    if not check_password(form_data.password, user.password_hash, user.salt):
        raise HTTPException(status_code=400, detail="Incorrect password or email")
    access_token = create_access_token(user_id=user.key_hash)
    # choose IP as device_id
    device_id = request.client.host
    refresh_token = await create_refresh_token(user.key_hash, device_id)
    return ItemUserLoginResult(user_id=user.key_hash, access_token=access_token, refresh_token=refresh_token)

@router.post("/user/refresh", response_model=ItemUserLoginResult)
async def refresh_token(refresh_token: ItemRefreshToken, request: Request, user_id: str = Depends(get_current_user)):
    device_id = request.client.host
    refresh_token_user_id = await verify_refresh_token(refresh_token.refresh_token, device_id)
    if refresh_token_user_id != user_id:
        raise HTTPException(status_code=400, detail="Invalid refresh token")
    access_token = create_access_token(user_id=user_id)
    new_refresh_token = await create_refresh_token(user_id, device_id)
    return ItemUserLoginResult(user_id=user_id, access_token=access_token, refresh_token=new_refresh_token)

@router.post("/user/logout", response_model=ItemUserRegisterResponse)
async def logout(refresh_token: ItemRefreshToken, session: SessionDep, user_id: str = Depends(get_current_user)):
    user = await session.scalar(select(User).filter(User.key_hash == user_id))
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    key = REDIS_KEY_REFRESH_TOKENS.format(token=generate_token_hash(refresh_token.refresh_token))
    await redis_handler.redis_cli.delete(key)
    return success_response(data=ItemUserRegisterResult(user_id=user.key_hash))

@router.get("/user/info", response_model=ItemUserInfoResponse)
async def user_info(session: SessionDep, user_id: str = Depends(get_current_user)):
    user = await session.scalar(select(User).filter(User.key_hash == user_id))
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return success_response(data=ItemUserInfoResult(user_id=user.key_hash, nick_name=user.nick_name, email=user.email))

@router.put("/user/info", response_model=ItemUserInfoResponse)
async def update_user_info(param: ItemUserRegisterRequest, session: SessionDep, user_id: str = Depends(get_current_user)):
    user = await session.scalar(select(User).filter(User.key_hash == user_id))
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    # Update user information here
    if param.nick_name:
        user.nick_name = param.nick_name
    if param.email:
        if await session.scalar(select(User).filter(User.email == param.email, User.key_hash != user_id)):
            return error_response(ErrorCodeEnum.InputParamsError, error_msg="Email already exists")
        user.email = param.email
    if param.password:
        salt = generate_random_hex()
        user.salt = salt
        user.password_hash = hash_password(param.password, salt)
    await session.commit()
    await session.refresh(user)
    return success_response(data=ItemUserInfoResult(user_id=user.key_hash, nick_name=user.nick_name, email=user.email))
