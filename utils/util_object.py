import re
import secrets


def camel_to_snake(name):
    """
    首字母大写字符串转下划线格式
    :param name:
    :return:
    """
    name = name.replace(' ', '_')

    # 处理驼峰命名的转换
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

def get_uuid():
    import uuid
    return str(uuid.uuid4())


def generate_random_hex(length=16):
    """Generate hex string. Default length is 16 bytes (32 hex characters)."""
    return secrets.token_hex(length)