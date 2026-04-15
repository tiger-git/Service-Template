import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from core.init_config import configure

class Log(logging.Logger):
    """
    日志配置
    """
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    FORMATTER: str = "%(name)s %(asctime)s [%(levelname)s] [%(filename)s] [%(lineno)s] %(message)s"

    def __init__(self):
        super(Log, self).__init__(configure.app_name or "service", level=getattr(logging, configure.log_level.upper(), logging.INFO))
        # file
        self.addHandler(self.file_handler())
        # console
        self.addHandler(self.console_handler())
        # include other package log
        # for name in ("fastmcp",):
        #     log = logging.getLogger(name)
        #     log.setLevel(configure.log_level.upper())
        #     log.addHandler(self)
      

    @staticmethod
    def file_handler():
        """
        文件格式打印日志
        :return:
        """
        base_dir = Path(__file__).resolve(strict=True).parent.parent
        if not os.path.exists("%s/logs" % base_dir):
            os.makedirs("%s/logs" % base_dir)
        path = os.path.join(base_dir, 'logs', f'{configure.log_file_name}.log')
        file_handler = RotatingFileHandler(
            path, maxBytes=1024 * 1024 * 10, backupCount=5)
        file_handler.setFormatter(logging.Formatter(
            Log.FORMATTER, datefmt=Log.DATETIME_FORMAT))
        return file_handler

    @staticmethod
    def console_handler():
        """
        控制台输出日志
        :return:
        """
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            Log.FORMATTER, datefmt=Log.DATETIME_FORMAT))
        return console_handler

logger = Log()