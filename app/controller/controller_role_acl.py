from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from core.handler.handler_role_acl import role_access_control
from core.handler.handler_user import RequireRole
from core.items.item_response import ItemCommonResponse
from core.services.handle_service import success_response, error_response
from core.items.enum_system import ErrorCodeEnum
from models.base import SessionDep
from models.role_acl import Access, GroupAccess, Role
from utils.util_log import logger

from core.items.item_role_acl import (
    ItemRole,
    ItemGroupAccess,
    ItemAccess,
    RoleListResult,
    RoleListResponse,
    GroupAccessListResult,
    GroupAccessListResponse,
    AccessListResult,
    AccessListResponse,
)

router = APIRouter()

# ====================== Role Management ======================
@router.get(
    "/roles",
    response_model=RoleListResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def get_role_access(
    session: SessionDep,
    role_id: int = None,
    role_name: str = None,
    search: str = None,
    page: int = 1,
    page_size: int = 10,
):
    roles, total = await role_access_control.role_get(
        session, search, role_id, role_name, page, page_size
    )
    roles = [ItemRole.model_validate(role, from_attributes=True) for role in roles]
    return success_response(data=RoleListResult(roles=roles, total=total))


@router.post(
    "/role",
    response_model=ItemCommonResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def add_role(session: SessionDep, role: ItemRole):
    row = await session.scalar(select(Role).filter(Role.role_name == role.role_name))
    if row:
        raise HTTPException(status_code=400, detail="Role already exists")
    row = Role(role_name=role.role_name, description=role.description)
    session.add(row)
    await session.commit()
    return success_response()


@router.put(
    "/role",
    response_model=ItemCommonResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def update_role(session: SessionDep, role: ItemRole, role_id: int):
    # check if role exists
    row = await session.scalar(
        select(Role).filter(Role.role_id != role_id, Role.role_name == role.role_name)
    )
    if row:
        raise HTTPException(status_code=400, detail="Role already exists")
    row: Role = await session.scalar(select(Role).filter(Role.role_id == role_id))
    if not role:
        raise HTTPException(status_code=400, detail="Role not found")
    # update role
    if row.role_name != role.role_name:
        row.role_name = role.role_name
    if row.description != role.description:
        row.description = role.description
    await session.commit()
    return success_response()


@router.delete(
    "/role",
    response_model=ItemCommonResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def delete_role(session: SessionDep, role_id):
    row = await session.scalar(select(Role).filter(Role.role_id == role_id))
    if not row:
        raise HTTPException(status_code=400, detail="Role not found")
    await session.delete(row)
    await session.commit()
    return success_response()

# ====================== Group Management ======================
@router.get(
    "/groups",
    response_model=GroupAccessListResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def get_group_access(
    session: SessionDep,
    group_id: int = None,
    group_name: str = None,
    search: str = None,
    page: int = 1,
    page_size: int = 10,
):
    groups, total = await role_access_control.group_access_get(
        session, search, group_id, group_name, page, page_size
    )
    groups = [
        ItemGroupAccess.model_validate(group, from_attributes=True) for group in groups
    ]
    return success_response(data=GroupAccessListResult(groups=groups, total=total))


@router.post(
    "/group",
    response_model=ItemCommonResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def add_group_access(session: SessionDep, group: ItemGroupAccess):
    row = await session.scalar(
        select(GroupAccess).filter(GroupAccess.group_name == group.group_name)
    )
    if row:
        raise HTTPException(status_code=400, detail="Group already exists")
    row = GroupAccess(group_name=group.group_name, description=group.description)
    session.add(row)
    await session.commit()
    return success_response()


@router.put(
    "/group",
    response_model=ItemCommonResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def update_group_access(
    session: SessionDep, group: ItemGroupAccess, group_id: int
):
    # check if group exists
    row = await session.scalar(
        select(GroupAccess).filter(
            GroupAccess.group_id != group_id, GroupAccess.group_name == group.group_name
        )
    )
    if row:
        raise HTTPException(status_code=400, detail="Group already exists")
    row: GroupAccess = await session.scalar(
        select(GroupAccess).filter(GroupAccess.group_id == group_id)
    )
    if not row:
        raise HTTPException(status_code=400, detail="Group not found")
    # update group
    if row.group_name != group.group_name:
        row.group_name = group.group_name
    if row.description != group.description:
        row.description = group.description
    await session.commit()
    return success_response()


@router.delete(
    "/group",
    response_model=ItemCommonResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def delete_group_access(session: SessionDep, group_id: int):
    row = await session.scalar(
        select(GroupAccess).filter(GroupAccess.group_id == group_id)
    )
    if not row:
        raise HTTPException(status_code=400, detail="Group not found")
    await session.delete(row)
    await session.commit()
    return success_response()

# ====================== Access Management ======================
@router.get(
    "/accesses",
    response_model=AccessListResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def get_access(
    session: SessionDep,
    access_id: int = None,
    access_name: str = None,
    search: str = None,
    page: int = 1,
    page_size: int = 10,
):
    accesses, total = await role_access_control.access_get(
        session, search, access_id, access_name, page, page_size
    )
    accesses = [
        ItemAccess.model_validate(access, from_attributes=True) for access in accesses
    ]
    return success_response(data=AccessListResult(accesses=accesses, total=total))


@router.post(
    "/access",
    response_model=ItemCommonResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def add_access(session: SessionDep, access: ItemAccess):
    row = await session.scalar(
        select(Access).filter(Access.access_name == access.access_name)
    )
    if row:
        raise HTTPException(status_code=400, detail="Access already exists")
    row = Access(access_name=access.access_name, description=access.description)
    session.add(row)
    await session.commit()
    return success_response()


@router.put(
    "/access",
    response_model=ItemCommonResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def update_access(session: SessionDep, access: ItemAccess, access_id: int):
    # check if access exists
    row = await session.scalar(
        select(Access).filter(
            Access.access_id != access_id, Access.access_name == access.access_name
        )
    )
    if row:
        raise HTTPException(status_code=400, detail="Access already exists")
    row: Access = await session.scalar(
        select(Access).filter(Access.access_id == access_id)
    )
    if not row:
        raise HTTPException(status_code=400, detail="Access not found")
    # update access
    if row.access_name != access.access_name:
        row.access_name = access.access_name
    if row.description != access.description:
        row.description = access.description
    await session.commit()
    return success_response()


@router.delete(
    "/access",
    response_model=ItemCommonResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def delete_access(session: SessionDep, access_id: int):
    row = await session.scalar(select(Access).filter(Access.access_id == access_id))
    if not row:
        raise HTTPException(status_code=400, detail="Access not found")
    await session.delete(row)
    await session.commit()
    return success_response()
# ====================== Role Bind Management ======================
@router.post(
    "/role/bind/access",
    response_model=ItemCommonResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def role_bind_access(session: SessionDep, role_id:int,access_id:int):
    await role_access_control.role_bind_access(
        session,
        access_id=access_id,
        role_id=role_id,
    )
    return success_response()

@router.delete(
    "/role/unbind/access",
    response_model=ItemCommonResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def role_unbind_access(session: SessionDep, role_id:int,access_id:int):
    await role_access_control.role_unbind_access(
        session,
        access_id=access_id,
        role_id=role_id,
    )
    return success_response()

@router.post(
    "/role/bind/group",
    response_model=ItemCommonResponse,
    dependencies=[Depends(RequireRole("admin"))])
async def role_bind_group(session: SessionDep, role_id:int,group_id:int):
    await role_access_control.role_bind_group_access(
        session,
        group_id=group_id,
        role_id=role_id,
    )
    return success_response()

@router.delete(
    "/role/unbind/group",
    response_model=ItemCommonResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def role_unbind_group(session: SessionDep, role_id:int,group_id:int):
    await role_access_control.role_unbind_group_access(
        session,
        group_id=group_id,
        role_id=role_id,
    )
    return success_response()

@router.post(
    "/group/bind/access",
    response_model=ItemCommonResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def group_bind_access(session: SessionDep, group_id:int,access_id:int):
    await role_access_control.group_bind_access(
        session,
        access_id=access_id,
        group_id=group_id,
    )
    return success_response()

@router.delete(
    "/group/unbind/access",
    response_model=ItemCommonResponse,
    dependencies=[Depends(RequireRole("admin"))],
)
async def group_unbind_access(session: SessionDep, group_id:int,access_id:int):
    await role_access_control.group_unbind_access(
        session,
        access_id=access_id,
        group_id=group_id,
    )
    return success_response()