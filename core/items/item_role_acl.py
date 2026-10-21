from typing import Any, Optional
from pydantic import BaseModel, Field

from .item_response import ItemCommonResponse

class ItemRole(BaseModel):
    role_id: int = Field(None, description="role id")
    role_name: str = Field(..., description="role name")
    description: str = Field(None, description="role description")

class ItemGroupAccess(BaseModel):
    group_name: str = Field(..., description="group name")
    description: str = Field(None, description="group description")

class ItemAccess(BaseModel):
    access_name: str = Field(..., description="access name")
    description: str = Field(None, description="access description")

class RoleListResult(BaseModel):
    roles: list[ItemRole]
    total:int = Field(..., description="Total number of roles")

class RoleListResponse(ItemCommonResponse):
    data: RoleListResult


class GroupAccessListResult(BaseModel):
    group_accesses: list[ItemGroupAccess]
    total:int = Field(..., description="Total number of group accesses")

class GroupAccessListResponse(ItemCommonResponse):
    data: GroupAccessListResult

class AccessListResult(BaseModel):
    accesses: list[ItemAccess]
    total:int = Field(..., description="Total number of accesses")

class AccessListResponse(ItemCommonResponse):
    data: AccessListResult