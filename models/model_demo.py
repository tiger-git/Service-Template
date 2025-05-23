from sqlalchemy import Column, String
from .base import Base


class User(Base):
    __tablename__ = 'user'
    key_hash = Column(String(32), primary_key=True,comment='primary_key hash')
    card_no = Column(String(18),comment='card number')
    nick_name = Column(String(10),comment='nick name')
    email = Column(String(20),comment='user email')
    password_hash = Column(String(32),comment='user password hash')

    def __repr__(self):
        return f'<User {self.key_hash}>'
