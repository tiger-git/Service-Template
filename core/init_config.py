from typing import Type, Tuple

from pydantic import Field, computed_field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)
from core.items.item_config import ItemConfigServices, ItemConfigSystem
from utils.util_object import camel_to_snake


class Configure(BaseSettings):
    """
    系统配置参数入口
    """

    # # 基于MSE的配置管理
    # system: ItemConfigSystem  # 系统参数配置【偏向内部业务】
    # sdk_services: ItemConfigServices  # sdk服务参数配置【偏向外部业务】

    # 基于环境变量.env
    # mysql config
    mysql_host: str = Field("localhost", description="mysql host")
    mysql_port: int = Field(3306, description="mysql port")
    mysql_user: str = Field("root", description="mysql user")
    mysql_password: str = Field("", description="mysql password")
    mysql_db: str = Field(..., description="mysql database")
    mysql_connect_url: str = Field("", description="mysql connection url")
    # redis config
    redis_host: str = Field("localhost", description="redis host")
    redis_port: int = Field(6379, description="redis port")
    redis_password: str = Field("", description="redis password")
    redis_db_index: int = Field(0, description="redis db index")
    redis_connect_url: str = Field("", description="redis connection url")
    # app config
    app_name: str = Field("Service", description="app name")
    docs_url: str | None = Field(None, description="docs url")
    redocs_url: str | None = Field(None, description="redocs url")
    log_level: str = Field("INFO", description="log level")

    @computed_field
    @property
    def log_file_name(self) -> str:
        """
        处理日志文件名
        :return:
        """
        return camel_to_snake(self.app_name)

    @computed_field
    @property
    def mysql_url(self) -> str:
        """
        relational database[mysql]
        :return:
        """
        if url := self.mysql_connect_url:
            return url
        url = (
            f"{self.mysql_user}:{self.mysql_password}@{self.mysql_host}/{self.mysql_db}"
        )
        return url

    @computed_field
    @property
    def redis_url(self) -> str:
        """
        non relational database[redis]
        :return:
        """
        if url := self.redis_connect_url:
            return url
        url = f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db_index}"
        return url

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
        )

    # # 加载MSE yaml 配置【TODO 自动拉取更新配置】
    # model_config = SettingsConfigDict(yaml_file="config.yaml")

    # @classmethod
    # def settings_customise_sources(
    #         cls,
    #         settings_cls: Type[BaseSettings],
    #         init_settings: PydanticBaseSettingsSource,
    #         env_settings: PydanticBaseSettingsSource,
    #         dotenv_settings: PydanticBaseSettingsSource,
    #         file_secret_settings: PydanticBaseSettingsSource,
    # ) -> Tuple[PydanticBaseSettingsSource, ...]:
    #     return (YamlConfigSettingsSource(settings_cls),)


configure = Configure()
