import sqlite3
from typing import Any, Dict, Generic, Iterator, List

from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import BaseMessage
from pydantic import BaseModel
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import StateSnapshot,Command

from utils.util_log import logger
from core.handler.handler_tools import get_weather,get_datetime,Decision
from core.init_config import configure
from core.services.service_models import ModelService, T
from core.items.item_llm_response import LLMResponse, WeatherAgentResponse

# from core.services.service_milvus import milvus_handler


class AgentResponse(BaseModel, Generic[T]):
    structured_response: T | None
    messages: List[BaseMessage]

class AgentService(ModelService[T]):
    def __init__(self, model, output_model, tools: List = []):
        super().__init__(model, output_model)
        self._checkpoint: SqliteSaver = None
        self.agent = create_agent(
            model=self.llm,
            tools=tools,
            system_prompt=self._system_prompt,
            response_format=self.output_model,
            checkpointer=self.checkpoint,  # checkpoint from SqliteSaver
        )

    @property
    def checkpoint(self):
        if self._checkpoint is None:
            conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
            checkpointer = SqliteSaver(conn)
            checkpointer.setup()
            self._checkpoint = checkpointer
        return self._checkpoint

    def get_messages(self,params:Dict[str, str],content:str=None):
        if content:
            return HumanMessagePromptTemplate.from_template(content).format_messages(**params)
        return self._human_prompt.format_messages(**params)

    def get_format_agent_response(self,result) -> AgentResponse[T]:
        result = AgentResponse.model_validate(result)
        return result
    
    def get_state(self,thread_id:str,checkpoint_id:str=None,is_history=False)->StateSnapshot|Iterator[StateSnapshot]:
        config = {"configurable": {"thread_id": thread_id}}
        if is_history:
            history_state = self.agent.get_state_history(config)
            return history_state
        if checkpoint_id:
            config["configurable"]["checkpoint_id"] = checkpoint_id
        current_state =  self.agent.get_state(config)
        return current_state


class ToolAgentService(AgentService[WeatherAgentResponse]):
    def __init__(self, model):
        super().__init__(model, WeatherAgentResponse, [get_weather,get_datetime])

    @property
    def llm(self):
        if self._model not in self._instince:
            self._instince[self._model] = ChatOpenAI(
                model=self._model,
                base_url=configure.bailian_api_base,
                api_key=configure.bailian_api_key,
            )
        return self._instince[self._model]


if __name__ == "__main__":
    thread_id = "8"
    service = ToolAgentService(configure.bailian_model)
    messages = service.get_messages({"question": "西安今天天气怎么样"})
    result = service.agent.invoke({"messages":messages},config={"configurable": {"thread_id": thread_id}})
    pending = result["__interrupt__"][0]
    assert pending.response_schema == Decision.model_json_schema() # 实际场景阻塞等待响应
    result = service.agent.invoke(Command(resume={"approved": True}), config={"configurable": {"thread_id": thread_id}})

    # checkpoint 短期记忆
    messages = service.get_messages({"question": "明天呢"})
    result = service.agent.invoke({"messages":messages}, config={"configurable": {"thread_id": thread_id}})
    pending = result["__interrupt__"][0]
    assert pending.response_schema == Decision.model_json_schema()
    result = service.agent.invoke(Command(resume={"approved": False}), config={"configurable": {"thread_id": thread_id}})
    
    # checkpoint 历史会话
    state = service.get_state(thread_id,is_history=True)

    # RAG
    # result = prompt_service.run_demo_rag_agent("最近要去北京出差，至少待3天，帮我规划下行程，并请帮我提供报销标准。注意出行当天往返地必须是晴天，接受顺延日期。")
    pass