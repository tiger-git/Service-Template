from abc import abstractmethod
import os
from typing import ClassVar, Dict, Generic, Type, TypeVar

from langchain.chat_models import BaseChatModel, init_chat_model
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from core.init_config import configure
from core.items.item_llm_response import LLMResponse
from utils.util_log import logger

T = TypeVar('T', bound=BaseModel)

class BaseAI(object):
    """AI 范畴基类组件
    - 提示词加载构建 https://docs.langchain.com/oss/python/langchain/messages#basic-usage

    Args:
        object (_type_): _description_

    Returns:
        _type_: _description_
    """
    def __init__(self):
        self._system_prompt = self.build_system_prompt()
        self._human_prompt = self.build_human_prompt()
    @classmethod
    def _read_prompt(cls,file_name):
        file_path = os.path.join(configure.base_dir,"static", "prompts", file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    @abstractmethod
    def build_system_prompt(self,*args,**kwargs)->str:
        """系统提示词，建议 SystemMessage 类型

        Returns:
            str: _description_
        """
        if content:=kwargs.get("content"):
            return SystemMessage(content=content)
        content =  "# Role \n\n You are a helpful assistant.\n\n"
        return SystemMessage(content=content)

    @abstractmethod
    def build_human_prompt(self,*args,**kwargs)->str:
        """用户提示词，建议 HumanMessagePromptTemplate 类型，或 (role, template_str)

        Returns:
            str: _description_
        """
        if content:= kwargs.get("content"):
            return HumanMessagePromptTemplate.from_template(content)
        content =  "question:\n\n{question}\n\n"
        return HumanMessagePromptTemplate.from_template(content)
        # return HumanMessage(content=content) # 无法处理参数传递

class ModelService(BaseAI,Generic[T]):
    """model 服务基类
        init model https://docs.langchain.com/oss/python/langchain/models#initialize-a-model

    Args:
        BaseAI (_type_): _description_
        Generic (_type_): _description_

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """
    _instince:ClassVar[Dict[str,BaseChatModel]] = {}

    def __init__(self,model:str,output_model:Type[T]):
        super().__init__()
        self.output_model=output_model
        self._model = model
        self._llm:BaseChatModel

    @property
    def llm(self):
        if self._model in self._instince:
            return self._instince[self._model]
        raise Exception

    def run(self,**params)->T:
        """

        Returns:
            T: _description_
        """
        model_with_structure  = self.llm.with_structured_output(self.output_model)
        chat_prompt  = ChatPromptTemplate.from_messages([self._system_prompt,self._human_prompt])

        # # # Method 1
        # message = chat_prompt.format_messages(**params)
        # result1 = model_with_structure.invoke(message)

        # Method 2 ->Chain LCEL
        chain = chat_prompt|model_with_structure
        result2 = chain.invoke(params)

        result = result2
        return result

class QwenModelService(ModelService[LLMResponse]):
    def __init__(self, model):
        super().__init__(model, LLMResponse)

    @property
    def llm(self):
        if self._model not in self._instince:
            self._instince[self._model] = ChatOpenAI(model=self._model,base_url=configure.bailian_api_base,api_key=configure.bailian_api_key)
        return self._instince[self._model]

if __name__ == "__main__":
    qwen_service = QwenModelService(configure.bailian_model)
    result = qwen_service.run(question="who are you")


        
