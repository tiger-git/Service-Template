from typing import List

from pymilvus import MilvusClient,DataType
from pymilvus.client.search_result import Hit

from core.handler.handler_chunk import chunk_handler
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
        self.create_collection(dimension=768, delete_existing=delete_existing)

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
        vector = chunk_handler.get_embeddings_by_ST([search_text])
        vector = chunk_handler.get_vector(vector[0][1])
        results = self.client.search(self.collection_name, [vector],output_fields=["content","file_name","doc_index"], limit=limit)
        data = results[0]
        return data

    def save_embeddings(self, text:str):
        embeddings = chunk_handler.split_and_embed(text)
        data = []
        for i, (chunk_text, vector) in enumerate(embeddings, start=1):
            data.append({
                # "id": i,
                "vector": chunk_handler.get_vector(vector),
                "content": chunk_text,
                "file_name": "static/docs/亿达科创差旅费管理制度.pdf",
                "doc_index":f'{i}/{len(embeddings)}'
            })
        result = self.client.insert(self.collection_name, data)
        return result

milvus_handler = MilvusHandler(client,delete_existing=False)

if __name__ == "__main__":
    from utils.util_file_parse import FileParse,FileSource
    # text = FileParse = FileParse.parse_file(FileSource.from_path("static/docs/亿达科创差旅费管理制度.pdf"))
    # text = FileParse = FileParse.parse_file(FileSource.from_path("static/docs/机票预订操作流程图解.pdf"))
    # milvus_handler.save_embeddings(text)
    result = milvus_handler.search("机票订购流程图解")
    # print(result)

   
    