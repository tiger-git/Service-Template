
from datetime import datetime
from typing import Literal

from langchain.tools import tool
from langgraph.types import interrupt
from pydantic import BaseModel

from utils.util_log import logger

class Decision(BaseModel):
    approved: bool
    note: str | None = None

@tool("get_weather_tool")
def get_weather(city:str,date:str)->Literal["sunny","cloudy","rainy","unknown"]:
    """get weather

    Args:
        city (str): city, like shanghai/上海
        date (str): date, like 2023-01-01

    Returns:
        _type_: _description_
    """
    logger.info(f"call get_weather_tool,{city},{date}")
    import random
    input = interrupt("query weather will cost some energy, do you want to query?",response_schema=Decision)
    if not input.approved:
        logger.info(f"city: {city}, date: {date}, weather query cancelled, note: {input.note}")
        return "unknown"

    if random.random() > 0.4:
        result = "sunny"
    elif random.random() < 0.3:
        result = "rainy"
    else:
        result = "cloudy"
    return result

@tool("get_datetime_tool")
def get_datetime(only_date):
    """get current datetime

    Args:
        only_date (_type_): value is date,like 2026-11-10

    Returns:
        _type_: datetime or date value
    """
    logger.info(f"call get_datetime_tool,{only_date}")
    now = datetime.now()
    if only_date:
        return now.strftime("%Y-%m-%d")
    return now.strftime("%Y-%m-%d %H:%M:%!S")
