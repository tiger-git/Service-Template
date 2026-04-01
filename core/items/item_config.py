from pydantic import BaseModel, Field
from .item_base import ItemBaseSDKUrl


class ItemConfigApp(BaseModel):
    title: str = Field('App')
    docs_url: str = Field('/docs')
    redoc_url: str = Field('/redoc')


class ItemConfigSystem(BaseModel):
    app: ItemConfigApp = Field(...)
    log_level: str = Field('info')


class ItemConfigServices(BaseModel):
    mysql: ItemBaseSDKUrl = Field(...,description='mysql service config')
    redis: ItemBaseSDKUrl = Field(...,description='redis service config')
