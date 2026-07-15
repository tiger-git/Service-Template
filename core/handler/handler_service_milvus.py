from typing import List

import dashscope
from pymilvus import MilvusClient,DataType
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymilvus.model.hybrid import BGEM3EmbeddingFunction
from pymilvus.client.search_result import Hit

from utils.util_log import logger

# Authentication not enabled
client = MilvusClient("http://localhost:19530")


# Authentication enabled with a non-root user
# client = MilvusClient(
#     uri="http://localhost:19530",
#     # token="user:password", # replace this with your token
#     db_name="default"
# )

class MilvusHandler:
    def __init__(self, client,collection_name="example_collection",delete_existing=False):
        self.client:MilvusClient = client
        self.collection_name = collection_name
        self.create_collection(dimension=1536, delete_existing=delete_existing)

    def create_collection(self, dimension,delete_existing=False):
        # Check if collection exists
        existing_collections = self.client.list_collections()
        if self.collection_name in existing_collections:
            logger.info(f"Collection '{self.collection_name}' already exists.")
            if not delete_existing:
                return
            logger.info(f"Deleting existing collection '{self.collection_name}'.")
            self.client.drop_collection(self.collection_name)
        schema = MilvusClient.create_schema(auto_id=True,enable_dynamic_field=True)
        schema.add_field("id", datatype=DataType.INT64, is_primary=True, auto_id=True)
        schema.add_field("vector", datatype=DataType.FLOAT_VECTOR, dim=dimension)
        schema.add_field("content", datatype=DataType.VARCHAR, max_length=2048)
        index_params = client.prepare_index_params()
        index_params.add_index("vector", index_type="AUTOINDEX", metric_type="COSINE")
        self.client.create_collection(self.collection_name, schema=schema, index_params=index_params)
        return


    def search(self, search_text, limit=10)->List[Hit]:
        query_vectors = self.get_embeddings([search_text])
        vector = query_vectors[0].get("embedding", [])
        results = self.client.search(self.collection_name, [vector],output_fields=["content","file_name"], limit=limit)
        data = results[0]
        return data

    def split_text_into_chunks(self,text, chunk_size=600, chunk_overlap=60):
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
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        使用 Milvus 提供的 BGEM3EmbeddingFunction 获取文本的向量表示
        """
        resp = dashscope.TextEmbedding.call(
                        model="text-embedding-v2",
                        input=texts,
                    )
        embeddings = resp.output.get("embeddings", [])
        # embedding_function = BGEM3EmbeddingFunction(use_fp16=False, device="cpu")
        # embeddings = embedding_function.encode_documents(texts)
        return embeddings

    def save_embeddings(self, texts: List[str]):
        embeddings = self.get_embeddings(texts)
        data = []
        for i, (text, vector) in enumerate(zip(texts, embeddings)):
            data.append({
                # "id": i,
                "vector": vector.get("embedding", []),
                "content": text,
                "file_name": "static/docs/亿达科创差旅费管理制度.pdf"
            })
        result = self.client.insert(self.collection_name, data)
        return result

milvus_handler = MilvusHandler(client,delete_existing=False)

if __name__ == "__main__":
    from utils.util_file_parse import FileParse,FileSource
    # text = FileParse = FileParse.parse_file(FileSource.from_path("static/docs/亿达科创差旅费管理制度.pdf"))
    text = FileParse = FileParse.parse_file(FileSource.from_path("static/docs/机票预订操作流程图解.pdf"))
    chunks = milvus_handler.split_text_into_chunks(text)
    milvus_handler.save_embeddings(chunks)
    result = milvus_handler.search("北京出差酒店费用报销标准")
    # print(result)

   
    