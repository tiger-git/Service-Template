from pydantic import BaseModel, Field
from .item_base import ItemBaseHost, ItemBaseSDKUrl


class ItemConfigApp(BaseModel):
    title: str = Field('App')
    docs_url: str = Field('/docs')
    redoc_url: str = Field('/redoc')


class ItemConfigSystem(BaseModel):
    app: ItemConfigApp = Field(...)
    log_level: str = Field('info')


class ItemConfigDB(ItemBaseHost, ItemBaseSDKUrl):
    port: int = Field(3306,description='service port')


class ItemConfigServices(BaseModel):
    mysql: ItemConfigDB = Field(...,description='mysql service config')
    redis: ItemConfigDB = Field(...,description='redis service config')
