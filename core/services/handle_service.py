from typing import Any
from core.items.enum_system import ErrorCodeEnum
from core.items.item_response import ItemCommonResponse


class ServiceError(Exception):
    """
    公共基础异常
    """

    def __init__(self, error: ErrorCodeEnum, error_msg: str):
        self.code, self.message = error.value
        self.error_msg = error_msg


def success_response(data: Any = None):
    """
    response is success
    :param data:
    :return:
    """
    code, message = ErrorCodeEnum.Success.value
    return ItemCommonResponse(code=code, message=message, data=data)


def error_response(code: ErrorCodeEnum, error_msg: str, data=None):
    """response is fail

    :param code: _description_
    :param error_msg: _description_
    :param data: _description_, defaults to None
    :return: _description_
    """
    return ItemCommonResponse(code=code.value[0], message=code.value[1], error_msg=error_msg, data=data)
