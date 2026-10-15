from pydantic import BaseModel, Field


class ItemBaseSDKUrl(BaseModel):
    url: str = Field(...,
                     description='sdk[redis/db/...] service connection url')


class ItemUserID(BaseModel):
    user_id: str = Field(..., description='user id')  # key hash


class ItemUserEmail(BaseModel):
    email: str = Field(..., description='user email')

class ItemAccessToken(BaseModel):
    access_token: str = Field(..., description='access token')

class ItemRefreshToken(BaseModel):
    refresh_token: str = Field(..., description='refresh token')


class ItemUserCardNo(BaseModel):
    """用户真实性，避免机器人或恶意用户
        仅注册时使用【TODO 安全性考虑】
    """
    card_no: str = Field(..., description='user card number')


class ItemUserNickName(BaseModel):
    nick_name: str = Field(None, description="user nick name")
