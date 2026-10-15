import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
import hmac
from fastapi import HTTPException,status,Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from core.items.constant import ACCESS_EXPIRE_MINUTES, ALGORITHM, REFRESH_EXPIRE_DAYS,REDIS_KEY_REFRESH_TOKENS,JWT_SECRET_KEY
from core.services.handle_service_redis import redis_handler

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