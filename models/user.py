from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    __tablename__ = "user"
    key_hash = Column(String(48), primary_key=True, comment="primary_key hash")
    nick_name = Column(String(64), comment="nick name")
    email = Column(String(64), comment="user email")
    password_hash = Column(String(64), comment="user password hash")
    salt = Column(String(32), comment="user salt")

    roles = relationship("Role", secondary="user_role", back_populates="users")

    def __repr__(self):
        return f"<User {self.key_hash}>"
