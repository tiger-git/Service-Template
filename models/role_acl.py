from sqlalchemy import Column, ForeignKey, String, Integer,Enum
from sqlalchemy.orm import relationship

from .base import Base

class Role(Base):
    __tablename__ = "role"
    role_id = Column(Integer, primary_key=True, autoincrement=True, comment="role id")
    role_name = Column(String(64), unique=True, comment="role name")
    description = Column(String(256), comment="role description")

    users = relationship("User", secondary="user_role", back_populates="roles")
    accesses = relationship("Access", secondary="role_access_control", back_populates="roles")
    groups = relationship("GroupAccess", secondary="role_group_access_control", back_populates="roles")

    def __repr__(self):
        return f"<Role {self.role_id}>"

class Access(Base):
    __tablename__ = "access"
    access_id = Column(Integer, primary_key=True, autoincrement=True, comment="access id")
    access_name = Column(String(64),unique=True, comment="access name")
    description = Column(String(256), comment="description")

    groups = relationship("GroupAccess", secondary="group_access_control", back_populates="accesses")
    roles = relationship("Role", secondary="role_access_control", back_populates="accesses")

    def __repr__(self):
        return f"<Access {self.access_id}>"

class GroupAccess(Base):
    __tablename__ = "group_access"
    group_id = Column(Integer, primary_key=True, autoincrement=True, comment="group id")
    group_name = Column(String(64), comment="group name")
    group_description = Column(String(256), comment="group description")

    accesses = relationship("Access", secondary="group_access_control", back_populates="groups")
    roles = relationship("Role", secondary="role_group_access_control", back_populates="groups")

    def __repr__(self):
        return f"<GroupAccess {self.group_id}>"
    
class GroupAccessControl(Base):
    __tablename__ = "group_access_control"
    group_access_control_id = Column(Integer, primary_key=True, autoincrement=True, comment="group access control id")
    group_id = Column(Integer, ForeignKey("group_access.group_id"), comment="foreign key to group_access")
    access_id = Column(Integer, ForeignKey("access.access_id"), comment="foreign key to access")

    def __repr__(self):
        return f"<GroupAccessControl {self.group_id}>"


class RoleAccessControl(Base):
    __tablename__ = "role_access_control"
    role_access_control_id = Column(Integer, primary_key=True, autoincrement=True, comment="role access control id")
    role_id = Column(Integer, ForeignKey("role.role_id"), comment="foreign key to role")
    access_id = Column(Integer, ForeignKey("access.access_id"), comment="foreign key to access")

    def __repr__(self):
        return f"<RoleAccessControl {self.role_id}>"

class RoleGroupAccessControl(Base):
    __tablename__ = "role_group_access_control"
    role_group_access_control_id = Column(Integer, primary_key=True, autoincrement=True, comment="role group access control id")
    role_id = Column(Integer, ForeignKey("role.role_id"), comment="foreign key to role")
    group_id = Column(Integer, ForeignKey("group_access.group_id"), comment="foreign key to group_access")

    def __repr__(self):
        return f"<RoleGroupAccessControl {self.role_id}>"


class UserRole(Base):
    __tablename__ = "user_role"
    user_role_id = Column(String(48), primary_key=True, comment="user role id")
    user_id = Column(String(48), ForeignKey("user.key_hash"), comment="foreign key to user")
    role_id = Column(Integer, ForeignKey("role.role_id"), comment="foreign key to role")

    def __repr__(self):
        return f"<UserRole {self.user_id}>"