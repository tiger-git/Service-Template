
from typing import Literal

from langchain.tools import tool

from utils.util_log import logger

@tool("get_weather_tool")
def get_weather(city:str,date:str)->Literal["sunny","cloudy","rainy"]:
    """get weather

    Args:
        city (str): city, like shanghai/上海
        date (str): date, like 2023-01-01

    Returns:
        _type_: _description_
    """
    import random
    if random.random() > 0.4:
        result = "sunny"
    elif random.random() < 0.3:
        result = "rainy"
    else:
        result = "cloudy"
    logger.info(f"city: {city}, date: {date}, weather result: {result}")
    return result
