from sqlalchemy import Column, String,Integer
from .base import Base


class User(Base):
    __tablename__ = "user"
    key_hash = Column(String(48), primary_key=True, comment="primary_key hash")
    nick_name = Column(String(64), comment="nick name")
    email = Column(String(64), comment="user email")
    password_hash = Column(String(64), comment="user password hash")
    salt = Column(String(32), comment="user salt")

    def __repr__(self):
        return f"<User {self.key_hash}>"
