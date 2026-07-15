import os
from typing import Literal

from jinja2 import Environment, FileSystemLoader
from langchain_core.messages import HumanMessage, SystemMessage,ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI # 或其他兼容 OpenAI 协议的模型
from langchain.tools import tool
from langchain.agents import create_agent

from core.init_config import configure
from utils.util_log import logger

# 导入你的 Pydantic 模型
from core.items.item_llm_response import AnswerResponse
from core.handler.handler_service_milvus import milvus_handler


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


class PromptService(object):
    def __init__(self, prompt_dir: str = "prompts"):
        prompt_dir = os.path.join(configure.base_dir, "static", prompt_dir)
        # 初始化 Jinja2 环境，启用自动转义防止注入
        self.jinja_env = Environment(
            loader=FileSystemLoader(prompt_dir),
            autoescape=True
        )
        # 初始化 LLM (示例使用 OpenAI，可替换为百炼/通义千问)
        self.llm = ChatOpenAI(model=configure.openai_model, temperature=0)

    def _get_template(self, filename: str):
        """获取并缓存模板内容"""
        return self.jinja_env.get_template(filename)

    def run_demo_rag(self, question: str) -> str:
        template = self._get_template("analyse_question.md.j2")
        user_level = "T-5"
        address = "西安"
        query_search_result = milvus_handler.search(question,limit=20)
        contents = [f"content: {x['entity']['content']}, file_name: {x['entity']['file_name']}" for x in query_search_result]
        # 渲染 Markdown 内容
        system_prompt_str = template.render(question=question,knowledge=contents,user_level=user_level,address=address)
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt_str)
        ])

        chain = prompt | self.llm.with_structured_output(AnswerResponse)
        result = chain.invoke({})
        return result

    def run_demo_rag_agent(self, question: str) -> AnswerResponse:
        """执行 示例步骤，返回结构化对象"""
        template = self._get_template("analyse_question.md.j2")
        user_level = "T-5"
        address = "西安"
        query_search_result = milvus_handler.search(question,limit=20)
        contents = [f"content: {x['entity']['content']}, file_name: {x['entity']['file_name']}" for x in query_search_result]
        # 渲染 Markdown 内容
        system_prompt_str = template.render(question=question,knowledge=contents,user_level=user_level,address=address)
        agent = create_agent(self.llm, tools=[get_weather])
        # 构建 LangChain Prompt
        messages = [
            SystemMessage(content=system_prompt_str), # 把 RAG 内容放在这里
            HumanMessage(content=question)
        ]

        result = agent.invoke({"messages": messages})
       
        structured_llm = self.llm.with_structured_output(AnswerResponse)
        final_result = structured_llm.invoke(result["messages"])
        return final_result
    


    

if __name__ == "__main__":
    prompt_service = PromptService()
    result = prompt_service.run_demo_rag_agent("最近要去北京出差，至少待3天，帮我规划下行程，并请帮我提供报销标准。注意出行当天往返地必须是晴天，接受顺延日期。")
    print(result.answer)