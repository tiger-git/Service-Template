from datetime import date

from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional

class AnswerResponse(BaseModel):
    """LLM 回答结构化对象"""
    answer: str = Field(..., description="LLM 的回答内容，markdown 格式")
    sources: List[str] = Field(..., description="LLM 回答依赖的数据源,相关文档名称")
    go_date: date = Field(None, description="出差日期")
    back_date: date = Field(None, description="返回日期")