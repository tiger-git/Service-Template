from datetime import date

from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional


class LLMResponse(BaseModel):
    answer: str = Field(description="answer")

class WeatherItem(BaseModel):
    date:str = Field(description="date str")
    weather:str = Field(description="weather")

class WeatherAgentResponse(LLMResponse):
    """LLM 回答结构化对象"""
    data:List[WeatherItem] = Field(description="weather data")

