from typing import Any, Optional
from pydantic import BaseModel, Field

from core.items.item_base import ItemUserID


class ItemCommonResponse(BaseModel):
    """
    公共response返回封装
    """
    code: str = Field(..., description="Business Code")
    message: str = Field(..., description="Business Description")
    error_msg: Optional[Any] = Field(None, description="Business Error info")
    data: Optional[Any] = Field(None, description="Business Data")


class ItemUserRegisterResult(ItemUserID):
    pass


class ItemUserRegisterResponse(ItemCommonResponse):
    data: ItemUserRegisterResult
