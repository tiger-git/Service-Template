import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
import hmac
from typing import Annotated
from fastapi import HTTPException,status,Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from core.items.constant import ACCESS_EXPIRE_MINUTES, REDIS_KEY_ROLE_ACCESSES, ALGORITHM, REFRESH_EXPIRE_DAYS,REDIS_KEY_REFRESH_TOKENS,JWT_SECRET_KEY
from core.services.handle_service_redis import redis_handler
from models.base import SessionDep
from models.role_acl import GroupAccess, Role
from models.user import User
from utils.util_log import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")

def generate_token_hash(token: str) -> str:
    """Generate a SHA-256 hash of the token."""
    return hashlib.sha256(token.encode()).hexdigest()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id

def check_password(password: str, password_hash: str, salt: str) -> bool:
    """Check if the password matches the hash."""
    return hmac.compare_digest(password_hash, hmac.new(salt.encode(), password.encode(), 'sha256').hexdigest())

def hash_password(password: str, salt: str) -> str:
    """Hash the password with the given salt."""
    return hmac.new(salt.encode(), password.encode(), 'sha256').hexdigest()


def create_access_token(**data) -> str:
    data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    return jwt.encode(
        data,
        JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )


async def create_refresh_token(user_id: str, device_id: str) -> str:
    raw = secrets.token_urlsafe(32)
    raw_hash = generate_token_hash(raw)
    data = {
        "user_id": user_id,
        "device_id": device_id,
        "expire_at": (datetime.now(timezone.utc) + timedelta(days=REFRESH_EXPIRE_DAYS)).isoformat(),
    }
    key = REDIS_KEY_REFRESH_TOKENS.format(token=raw_hash)
    await redis_handler.redis_cli.set(key, json.dumps(data), ex=timedelta(days=REFRESH_EXPIRE_DAYS))
    return raw

async def get_role_accesses(session: SessionDep,role: Role=None,role_name: str=None) -> set[str]:
    if role:
        role_name = role.role_name
    if not role_name:
        logger.warning("No role or role_name provided to get_role_accesses.")
    accesses = set()
    key = REDIS_KEY_ROLE_ACCESSES.format(role_name=role_name)

    # check redis cache first
    cached_accesses = await redis_handler.redis_cli.get(key)
    if cached_accesses:
        return set(json.loads(cached_accesses))
    if role_name:
        role = await session.scalar(
            select(Role).options(selectinload(Role.accesses),selectinload(Role.groups).selectinload(GroupAccess.accesses)
                                 ).filter(Role.role_name == role_name))
        role_accesses = {access.access_name for access in role.accesses}
        accesses.update(role_accesses)
        for group in role.groups:
            accesses.update({access.access_name for access in group.accesses})

    if accesses:
        # set redis cache
        await redis_handler.redis_cli.set(key, json.dumps(list(accesses)), ex=timedelta(minutes=5))
        return accesses
    return set()

async def verify_refresh_token(raw_token: str, device_id: str) -> str:
    raw_hash = generate_token_hash(raw_token)
    key = REDIS_KEY_REFRESH_TOKENS.format(token=raw_hash)
    record = await redis_handler.redis_cli.get(key)
    if not record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    try:
        record = json.loads(record)
        expire_at = datetime.fromisoformat(record["expire_at"])
        if datetime.now(timezone.utc) > expire_at:
            await redis_handler.redis_cli.delete(key)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
        if record["device_id"] != device_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Device mismatch")
        return record["user_id"]
    except (KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

class RequireRole(object):
    def __init__(self, *roles: str):
        self.roles = set(roles)

    async def __call__(self, user_id: Annotated[str, Depends(get_current_user)],session: SessionDep) -> User:
        user = await session.scalar(
            select(User).options(selectinload(User.roles)
                                 ).filter(User.key_hash == user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        roles = {role.role_name for role in user.roles}
        if not self.roles.issubset(roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
            )
        return user

class RequireAccess(RequireRole):
    def __init__(self, *accesses: str):
        self.accesses = set(accesses)

    async def __call__(self, user_id: Annotated[str, Depends(get_current_user)],session: SessionDep) -> User:
        user = await session.scalar(
            select(User).options(selectinload(User.roles)
                                 ).filter(User.key_hash == user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        roles = user.roles
        accesses = set()
        for role in roles:
            role:Role
            role_accesses = await get_role_accesses(session, role=role)
            if role_accesses:
                accesses.update(role_accesses)
        if not self.accesses.issubset(accesses):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
            )
        return user