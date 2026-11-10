from datetime import date

from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Union


class LLMResponse(BaseModel):
    answer: str = Field(description="answer")

class WeatherItem(BaseModel):
    date:str = Field(description="date str")
    weather:str = Field(description="weather")

class WeatherAgentResponse(LLMResponse):
    """LLM 回答结构化对象"""
    data: Union[List[WeatherItem], None] = Field(default_factory=list,description="weather data")

