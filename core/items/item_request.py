from pydantic import BaseModel, Field
from .item_base import ItemUserEmail, ItemUserCardNo, ItemUserNickName


class ItemUserRegisterRequest(ItemUserEmail, ItemUserCardNo, ItemUserNickName):
    pass
