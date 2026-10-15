from pydantic import BaseModel, Field
from .item_base import ItemUserEmail, ItemUserCardNo, ItemUserNickName


class ItemUserRegisterRequest(ItemUserEmail, ItemUserNickName):
    password: str = Field(..., description="user password")

class ItemUserLoginRequest(BaseModel):
    username: str = Field(..., description="user email")
    password: str = Field(..., description="user password")
