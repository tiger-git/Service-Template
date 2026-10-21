from enum import Enum,unique


@unique
class ErrorCodeEnum(Enum):
    """
    通用Response Code码和含义
    """
    Success = '0000','success'

    InputParamsError = '1002','input params error'

    SDKMysqlError = '2101', 'mysql error'  # mysql 相关错误
    SDKRedisError = '2201', 'redis error'  # redis 相关错误

    ServiceRateLimit = '3429', 'sdk rate limit'  # 三方服务限频，例如openapi

    SystemRateLimit = '9429', 'system API rate limit'  # 己方限频
    SystemParamsError = '9001','system params error'
    SystemError = '9999','system unknown error'

@unique
class RoleEnum(Enum):
    """
    角色枚举
    """
    SuperAdmin = 'super_admin' # 超级管理员
    Admin = 'admin' # 管理员
    Normal = 'normal' # 普通用户

@unique
class AccessEnum(Enum):
    """
    权限枚举
    """
    UserDelete = 'user:delete' # 删除用户
