import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.orm.session import Session

from config import configure

engine = create_async_engine(
    f'mysql+aiomysql://{configure.mysql_url}',
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
local_session = sessionmaker(
    autocommit=False, autoflush=False, class_=AsyncSession, bind=engine)


async def get_session():
    async with local_session() as db:
        print(f"new db session {id(db)}")
        yield db

SessionDep = Annotated[Session, Depends(get_session)]


def get_current_time(): return datetime.datetime.now(datetime.timezone.utc)


class Base(DeclarativeBase):
    created_time = Column(DateTime(True), default=get_current_time)
    updated_time = Column(
        DateTime(True), default=get_current_time, onupdate=get_current_time)
