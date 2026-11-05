import os
from typing import Any, List,Tuple

import numpy
import dashscope
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from modelscope import snapshot_download
from pymilvus.model.hybrid import BGEM3EmbeddingFunction

from core.init_config import configure
from utils.util_log import logger


class ChunkHandler(object):
    """chunk handler for text splitting and embedding generation"""

    def __init__(self, model_name: str = "Qwen/Qwen3-Embedding-0.6B",dim=768):
        """_summary_

        Args:
            model_name (str, optional): _description_. Defaults to "Qwen/Qwen3-Embedding-0.6B".
            dim (int, optional): _description_. Defaults to 768.
        """
        self.model_name = model_name
        self.dim = dim
        self._bge_embedding_function = None
        self._model = None

    @classmethod
    def _model_path(cls, model_name: str) -> str:
        return os.path.join(configure.local_model_path, model_name)

    @classmethod
    def ensure_model(cls, model_name: str) -> str:
        model_path = cls._model_path(model_name)
        """check if the model exists in the local path, if not, download it from modelscope"""
        try:
            model_path = os.path.join(configure.local_model_path, model_name)
            if not os.path.exists(model_path):
                logger.info(f"Model directory '{model_path}' does not exist. Downloading model...")
                snapshot_download(model_name, cache_dir=configure.local_model_path)
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model directory '{model_path}' does not exist after download.")
            return model_path
        except Exception as e:
            logger.error(f"Error confirming model '{model_name}': {e}")
            raise

    @property
    def model(self):
        if self._model is None:
            model_path = self.ensure_model(self.model_name)
            self._model = SentenceTransformer(model_path,truncate_dim=self.dim)
            embed_dim = self.model.get_embedding_dimension()
            logger.info(f"Loaded embedding model '{self.model_name}' with dimension {embed_dim}")
        return self._model

    @property
    def bge_embedding_function(self):
        if self._bge_embedding_function is None:
            model_path = self.ensure_model(self.model_name)
            self._bge_embedding_function = BGEM3EmbeddingFunction(model_name=model_path, device="cpu",truncate_dim=self.dim)
        return self._bge_embedding_function

    @staticmethod
    def get_vector(vector:Any) -> List[float]:
        """clean vector

        Args:
            vector (Any): _description_

        Returns:
            List[float]: _description_
        """
        if isinstance(vector, List):
            if isinstance(vector[0], float):
                return vector
            if isinstance(vector[0], numpy.float32):
                new_vector = list(map(float, vector))
                return new_vector
            return vector
        if isinstance(vector, numpy.ndarray):
            return vector.tolist()
        return vector

    def split_text_into_chunks(self, text, chunk_size=600, chunk_overlap=60):
        """
        使用递归字符切片器进行切片
        chunk_size: 每个分块的最大字符数
        chunk_overlap: 前后分块的重叠字数，防止上下文在切点处断裂
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", " ", ""]
        )
        chunks = text_splitter.split_text(text)
        return chunks

    def get_embeddings_by_dashscope(self, texts: List[str]) -> List[List[float]]:
        """get embeddings using dashscope,requires dashscope account and api_key
            - DASHSCOPE_API_KEY

        Args:
            texts (List[str]): _description_

        Returns:
            List[List[float]]: _description_
        """
        resp = dashscope.TextEmbedding.call(
            model="text-embedding-v2",
            input=texts,
        )
        embeddings = resp.output.get("embeddings", [])
        return embeddings
    
    def get_embeddings_by_ST(self, texts: list[str]) -> List[Tuple[str, List[float]]]:
        """get embeddings using SentenceTransformer,requires the model to be downloaded from modelscope and stored in local path
            - MODEL_PATH

        Args:
            texts (list[str]): _description_

        Returns:
            List[Tuple[str, List[float]]]: _description_
        """
        vectors = self.model.encode(texts, normalize_embeddings=True)
        embeddings = vectors.tolist()
        data = list(zip(texts, embeddings))
        return data

    def get_embeddings_by_BGE(self, texts: list[str]) -> List[Tuple[str, List[float]]]:
        """get embeddings using BGE,requires the model to be downloaded from modelscope and stored in local path
            - MODEL_PATH

        Args:
            texts (list[str]): _description_

        Returns:
            List[Tuple[str, List[float]]]: _description_
        """
        vectors = self.bge_embedding_function.encode_documents(texts)
        embeddings = vectors["dense"]
        # embeddings = list(map(self.get_vector, embeddings))
        data = list(zip(texts, embeddings))
        return data

    def split_and_embed(self, text: str, chunk_size=600, chunk_overlap=60) -> List[Tuple[str, List[float]]]:
        """_summary_

        Args:
            text (str): _description_
            chunk_size (int, optional): _description_. Defaults to 600.
            chunk_overlap (int, optional): _description_. Defaults to 60.

        Returns:
            List[Tuple[str, List[float]]]: _description_
        """
        chunks = self.split_text_into_chunks(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        # embeddings = self.get_embeddings_by_dashscope(chunks)
        embeddings_v1 = self.get_embeddings_by_ST(chunks)
        # embeddings_v2 = self.get_embeddings_by_BGE(chunks)

        embeddings = embeddings_v1
        return embeddings

chunk_handler = ChunkHandler("BAAI/bge-base-zh-v1.5")

if __name__ == "__main__":
    from utils.util_file_parse import FileParse,FileSource
    text = FileParse = FileParse.parse_file(FileSource.from_path("static/docs/机票预订操作流程图解.pdf"))
    data = chunk_handler.split_and_embed(text)