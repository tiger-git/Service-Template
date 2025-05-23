from typing import Type, Tuple

from pydantic import computed_field
from pydantic_settings import (
    BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, YamlConfigSettingsSource,
)
from core.items.item_config import ItemConfigSystem, ItemConfigServices
from utils.util_object import camel_to_snake

CONFIG_PATH = 'config/config.yaml'


class Configure(BaseSettings):
    """
    系统配置参数入口
    """
    system: ItemConfigSystem  # 系统参数配置【偏向内部业务】
    sdk_services: ItemConfigServices  # sdk服务参数配置【偏向外部业务】

    @computed_field
    @property
    def log_file_name(self) -> str:
        """
        处理日志文件名
        :return:
        """
        return camel_to_snake(self.system.app.title)

    @computed_field
    @property
    def mysql_url(self) -> str:
        """
        relational database[mysql]
        :return:
        """
        if url:=self.sdk_services.mysql.url:
            return url
        conf = self.sdk_services.mysql
        url = f"{conf.user}:{conf.password}@{conf.host}/{conf.database}"
        return url

    @computed_field
    @property
    def redis_url(self) -> str:
        """
        non relational database[redis]
        :return:
        """
        if url:=self.sdk_services.redis.url:
            return url
        conf = self.sdk_services.redis
        url = f"{conf.password}@{conf.host}:{conf.port}/{conf.db_index}"
        url = f"redis://{url}"
        return url

    model_config = SettingsConfigDict(yaml_file=CONFIG_PATH)

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)


configure = Configure()
