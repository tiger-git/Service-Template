from typing import Dict, Generic, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI # 或其他兼容 OpenAI 协议的模型
from langchain.agents import create_agent
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from core.handler.handler_tools import get_weather
from core.init_config import configure
from utils.util_log import logger
from core.services.service_models import ModelService,T
from core.items.item_llm_response import LLMResponse
# from core.services.service_milvus import milvus_handler


class AgentResponse(BaseModel,Generic[T]):
    structured_response:T|None
    messages:List[BaseMessage]


class AgentService(ModelService[T]):
    def __init__(self, model, output_model,tools:List=[]):
        super().__init__(model, output_model)
        self.tools = tools

    def run(self,params: Dict[str, str]={})->AgentResponse[T]:
        chat_prompt  = ChatPromptTemplate.from_messages([self._system_prompt,self._human_prompt])
        messages = chat_prompt.format_messages(**params)
        agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self._system_prompt,
            response_format=self.output_model,
        )
        result = agent.invoke({"messages":messages})
        result = AgentResponse.model_validate(result)
        return result


class ToolAgentService(AgentService[LLMResponse]):
    def __init__(self, model):
        super().__init__(model, LLMResponse,[])

        # TODO 工具会对结构化输出有影响，结果是None,但messages数据正常
        # super().__init__(model, LLMResponse,[get_weather])

    @property
    def llm(self):
        if self._model not in self._instince:
            self._instince[self._model] = ChatOpenAI(model=self._model,base_url=configure.bailian_api_base,api_key=configure.bailian_api_key)
        return self._instince[self._model]

if __name__ == "__main__":
    demo = ToolAgentService(configure.bailian_model)
    result = demo.run({"question":"今天2026-11-5，西安接下来3天的天气如何?"})
    print(result)
    # result = prompt_service.run_demo_rag_agent("最近要去北京出差，至少待3天，帮我规划下行程，并请帮我提供报销标准。注意出行当天往返地必须是晴天，接受顺延日期。")
