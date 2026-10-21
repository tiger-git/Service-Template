"""TODO 角色权限，中台或后台维护"""

from typing import Tuple,List

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from models.base import SessionDep
from models.role_acl import Access, GroupAccess, Role
from models.user import User
from utils.util_log import logger

class RoleAccessControl(object):
    """角色权限"""

    async def get_role(self, session: SessionDep, role_id: int = None, role_name: str = None):
        """获取角色"""
        query = select(Role).options(selectinload(Role.accesses),selectinload(Role.groups).selectinload(GroupAccess.accesses))
        if role_id:
            query = query.filter(Role.role_id == role_id)
        elif role_name:
            query = query.filter(Role.role_name == role_name)
        else:
            logger.warning("get_role: role_id or role_name must be provided")
            return None
        role = await session.scalar(query)
        if not role:
            logger.warning("get_role: role not found")
            return None
        return role

    async def get_access(self, session: SessionDep, access_id: int = None, access_name: str = None):
        """获取权限"""
        query = select(Access)
        if access_id:
            query = query.filter(Access.access_id == access_id)
        elif access_name:
            query = query.filter(Access.access_name == access_name)
        else:
            logger.warning("get_access: access_id or access_name must be provided")
            return None
        access = await session.scalar(query)
        if not access:
            logger.warning("get_access: access not found")
            return None
        return access

    async def get_group_access(self, session: SessionDep, group_id: int = None, group_name: str = None):
        """获取权限组"""
        query = select(GroupAccess)
        if group_id:
            query = query.filter(GroupAccess.group_id == group_id)
        elif group_name:
            query = query.filter(GroupAccess.group_name == group_name)
        else:
            logger.warning("get_group_access: group_id or group_name must be provided")
            return None
        group_access = await session.scalar(query)
        if not group_access:
            logger.warning("get_group_access: group_access not found")
            return None
        return group_access

    async def role_add(self, session: SessionDep,role_name: str, description: str = None):
        """添加角色"""
        role = Role(role_name=role_name, description=description)
        session.add(role)
        await session.commit()
        return role

    async def role_delete(self, session: SessionDep, role_id: int= None, role_name: str= None):
        """删除角色"""
        query = select(Role)
        role = await self.get_role(session, role_id=role_id, role_name=role_name)
        if not role:
            return None
        await session.delete(role)
        await session.commit()
        return role

    async def role_update(self, session: SessionDep,new_role_name: str = None, description: str = None, role_id: int = None, role_name: str = None):
        """更新角色"""
        role = await self.get_role(session, role_id=role_id, role_name=role_name)
        if not role:
            return None
        if new_role_name:
            role.role_name = new_role_name
        if description:
            role.description = description
        await session.commit()
        return role

    async def role_get(self,session: SessionDep,search: str = None, role_id: int = None, role_name: str = None,page: int = 1, page_size: int = 10)->Tuple[List[Role],int]:
        """获取角色"""
        query = select(Role)
        if role_id:
            query = query.filter(Role.role_id == role_id)
        elif role_name:
            query = query.filter(Role.role_name == role_name)
        elif search:
            query = query.filter(Role.role_name.like(f"%{search}%"))
        total = await session.scalar(select(func.count()).select_from(query.subquery()))
        roles = await session.scalars(query.offset((page - 1) * page_size).limit(page_size))
        return roles.all(), total

    async def group_access_get(self,session: SessionDep,search: str = None, group_id: int = None, group_name: str = None,page: int = 1, page_size: int = 10)->Tuple[List[GroupAccess],int]:
        """获取权限组"""
        query = select(GroupAccess).options(selectinload(GroupAccess.accesses))
        if group_id:
            query = query.filter(GroupAccess.group_id == group_id)
        elif group_name:
            query = query.filter(GroupAccess.group_name == group_name)
        elif search:
            query = query.filter(GroupAccess.group_name.like(f"%{search}%"))
        total = await session.scalar(select(func.count()).select_from(query.subquery()))
        groups = await session.scalars(query.offset((page - 1) * page_size).limit(page_size))
        return groups.all(), total

    async def access_get(self,session: SessionDep,search: str = None, access_id: int = None, access_name: str = None,page: int = 1, page_size: int = 10)->Tuple[List[Access],int]:
        """获取权限"""
        query = select(Access)
        if access_id:
            query = query.filter(Access.access_id == access_id)
        elif access_name:
            query = query.filter(Access.access_name == access_name)
        elif search:
            query = query.filter(Access.access_name.like(f"%{search}%"))
        total = await session.scalar(select(func.count()).select_from(query.subquery()))
        accesses = await session.scalars(query.offset((page - 1) * page_size).limit(page_size))
        return accesses.all(), total

    async def role_bind_access(self, session: SessionDep,access_id: int = None,access_name: str = None, role_id: int = None, role_name: str = None):
        """绑定角色权限"""
        role = await self.get_role(session, role_id=role_id, role_name=role_name)
        if not role:
            return None
        access = await self.get_access(session, access_id=access_id, access_name=access_name)
        if not access:
            return None
        role.accesses.append(access)
        await session.commit()
        return

    async def role_unbind_access(self, session: SessionDep,access_id: int = None,access_name: str = None, role_id: int = None, role_name: str = None):
        """解绑角色权限"""
        role = await self.get_role(session, role_id=role_id, role_name=role_name)
        if not role:
            return None
        access = await self.get_access(session, access_id=access_id, access_name=access_name)
        if not access:
            return None
        role.accesses.remove(access)
        await session.commit()
        return

    async def role_bind_group_access(self, session: SessionDep,group_id: int = None,group_name: str = None, role_id: int = None, role_name: str = None):
        """绑定角色权限组"""
        role = await self.get_role(session, role_id=role_id, role_name=role_name)
        if not role:
            return None
        group_access = await self.get_group_access(session, group_id=group_id, group_name=group_name)
        if not group_access:
            return None
        role.groups.append(group_access)
        await session.commit()
        return

    async def role_unbind_group_access(self, session: SessionDep,group_id: int = None,group_name: str = None, role_id: int = None, role_name: str = None):
        """解绑角色权限组"""
        role = await self.get_role(session, role_id=role_id, role_name=role_name)
        if not role:
            return None
        group_access = await self.get_group_access(session, group_id=group_id, group_name=group_name)
        if not group_access:
            return None
        role.groups.remove(group_access)
        await session.commit()
        return

    async def user_bind_role(self, session: SessionDep, user_id: int, role_id: int = None, role_name: str = None):
        """绑定用户角色"""
        role = await self.get_role(session, role_id=role_id, role_name=role_name)
        if not role:
            return None
        user = await session.get(User, user_id)
        if not user:
            logger.warning("user_bind_role: user not found")
            return None
        user.roles.append(role)
        await session.commit()
        return

    async def user_unbind_role(self, session: SessionDep, user_id: int, role_id: int = None, role_name: str = None):
        """解绑用户角色"""
        role = await self.get_role(session, role_id=role_id, role_name=role_name)
        if not role:
            return None
        user = await session.get(User, user_id)
        if not user:
            logger.warning("user_unbind_role: user not found")
            return None
        user.roles.remove(role)
        await session.commit()
        return

    async def group_bind_access(self, session: SessionDep, access_id: int = None,access_name: str = None, group_id: int = None, group_name: str = None):
        """绑定权限组权限"""
        group_access = await self.get_group_access(session, group_id=group_id, group_name=group_name)
        if not group_access:
            return None
        access = await self.get_access(session, access_id=access_id, access_name=access_name)
        if not access:
            return None
        group_access.accesses.append(access)
        await session.commit()
        return

    async def group_unbind_access(self, session: SessionDep, access_id: int = None,access_name: str = None, group_id: int = None, group_name: str = None):
        """解绑权限组权限"""
        group_access = await self.get_group_access(session, group_id=group_id, group_name=group_name)
        if not group_access:
            return None
        access = await self.get_access(session, access_id=access_id, access_name=access_name)
        if not access:
            return None
        group_access.accesses.remove(access)
        await session.commit()
        return


role_access_control = RoleAccessControl()