from collections import defaultdict
import random
from typing import List

from elasticsearch import Elasticsearch
from elasticsearch import dsl
from elasticsearch.dsl.query import Match
from elasticsearch.dsl import Document,connections,mapped_field

from core.handler.handler_chunk import chunk_handler
from utils.util_log import logger


api_key = "eUgxNm42RUJpYmhfYTVkMVRjRng6QURhSjFxT3BlUnV3a2t3Tk0zUUpidw=="

class ESService:
    NUMBER_OF_REPLICAS = 0

    def __init__(self,api_key: str = None):
        self.init_client(api_key=api_key)
        self.ping()

    def ping(self):
        if self.client.ping():
            logger.info("✅ 成功连接到 Elasticsearch")
        else:
            logger.error("❌ 无法连接 Elasticsearch")
            raise ConnectionError(
                "无法连接 Elasticsearch，请检查服务是否启动或网络连接是否正常。"
            )

    def init_client(self, url: str = None,api_key: str = None):
        # basic_auth = ("elastic", "your_password")  # 替换为你的用户名和密码
        # client = Elasticsearch(url or "http://127.0.0.1:9200",basic_auth=basic_auth)
        client = Elasticsearch(url or "http://127.0.0.1:9200",api_key=api_key)
        self.client = client

    def create_index(self, index_name: str, mapping: dict = None):
        try:
            if self.client.indices.exists(index=index_name):
                logger.info(f"Index '{index_name}' already exists.")
                return
            if mapping:
                result = self.client.indices.create(index=index_name, body=mapping,settings={"number_of_replicas": self.NUMBER_OF_REPLICAS})
            else:
                result = self.client.indices.create(
                    index=index_name,
                    settings={"number_of_replicas": self.NUMBER_OF_REPLICAS},
                )
            if result.get("acknowledged") and result.get("shards_acknowledged"):
                logger.info(f"Index '{index_name}' created successfully.")
            else:
                logger.error(
                    f"Failed to create index '{index_name}'., Result: {result}"
                )
        except Exception as e:
            logger.error(f"Error creating index: {e}")

    def save_document(self, index_name: str, document: dict):
        try:
            result = self.client.index(index=index_name, body=document)
            logger.info(f"Document indexed successfully: {result}")
        except Exception as e:
            logger.error(f"Error indexing document: {e}")
        finally:
            self.client.indices.refresh(index=index_name)

    def search_documents(self, index_name: str, query: dict):
        try:
            result = self.client.search(index=index_name, body=query)
            hits = result.get("hits")
            if not hits:
                logger.error(f"No documents found.result: {result}")
                return []
            total_hits = hits["total"]["value"]
            logger.info(f"Search completed. Found {total_hits} documents.")
            result.body
            return hits["hits"]
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    def demo_create_index(self, index_name: str):
        mapping = {
            "mappings": {
                "properties": {
                    "text": {"type": "text"},  # 用于关键字搜索
                    "embedding": {  # 用于向量搜索
                        "type": "dense_vector",
                        "dims": 768,  # 必须与你的 Embedding 模型维度一致
                        "index": True,
                        "similarity": "cosine",  # 余弦相似度
                    },
                    "file_name": {"type": "keyword"},  # 元数据过滤
                }
            }
        }
        self.create_index(index_name, mapping)

    def demo_save(self, index_name: str):
        self.save_document(
            index_name,
            {
                "text": "这是一个示例文档。",
                "embedding": [0.1] * 768,  # 示例向量，实际应为模型生成的向量
                "file_name": "example.txt",
            },
        )
    def demo_query(self, index_name: str):
        search_query = {
            "query": {
                "match": {
                    "text": {
                        "query": "RAG 怎么减少 AI 幻觉？",
                        "fuzziness": "AUTO",  # 开启模糊匹配，防止关键词拼写错误
                    }
                }
            },
            "knn": {
                "field": "embedding",
                "query_vector": [0.95] * 768,  # 替换为当前问题的真实 768 维向量
                "k": 10,  # 向量召回 Top 10
                "num_candidates": 100,  # 预召回候选数，越大越准，但越慢
            },
            # 6. 使用 RRF (Reciprocal Rank Fusion) 融合两路结果
            # "rank": {"rrf": {"rank_constant": 60, "window_size": 100}},
        }
        results = self.search_documents(index_name, search_query)

    def clear_index(self,index_name:str,only_data:bool=False):
        if only_data:
            try:
                self.client.delete_by_query(index=index_name, body={"query": {"match_all": {}}})
                logger.info(f"All documents in index '{index_name}' have been deleted.")
            except Exception as e:
                logger.error(f"Error deleting documents from index '{index_name}': {e}")
        else:
            try:
                self.client.indices.delete(index=index_name)
                logger.info(f"Index '{index_name}' has been deleted.")
            except Exception as e:
                logger.error(f"Error deleting index '{index_name}': {e}")

connections.create_connection(hosts="http://localhost:9200",api_key=api_key)

class ESIndexArticle(Document):
    """推荐

    Args:
        Document (_type_): _description_
    """
    text:str = mapped_field(dsl.Text())
    file_name:str = mapped_field(dsl.Keyword())
    embedding:List[float] = mapped_field(dsl.DenseVector(dims=768, index=True, similarity="cosine"))

    class Index:
        name = "knowledge_article"
        settings = {
            "number_of_replicas": ESService.NUMBER_OF_REPLICAS,
        }
def rrf_fusion(rank_lists: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """RRF (Reciprocal Rank Fusion) 融合算法

    Args:
        rank_lists (list[list[str]]): _description_
        k (int, optional): _description_. Defaults to 60.

    Returns:
        list[tuple[str, float]]: _description_
    """
    scores: dict[str, float] = defaultdict(float)

    for items in rank_lists:
        for rank, doc_id in enumerate(items, start=1):
            scores[doc_id] += 1.0 / (k + rank)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def save(text:str):
    ESIndexArticle.init()
    embedding = chunk_handler.split_and_embed(text)
    for meta_id, (chunk_text, vector) in enumerate(embedding,start=1):
        # meta_id = random.randint(1, 1000)  # 随机生成一个 ID
        article = ESIndexArticle(
            text=chunk_text,
            embedding=chunk_handler.get_vector(vector),
            file_name=f"example_{meta_id}.txt",
            meta={"id": meta_id}
        )
        article.save()
    row = ESIndexArticle.get(id=meta_id)
    row.update(file_name=f"updated_example.txt.{random.randint(1, 100)}")
    return

def search(query:str):
    # TODO bug-中文转义会有问题
    # query = ESIndexArticle.esql_from().where(functions.match(ESIndexArticle.text, "示例")).limit(10)
    # results = ESIndexArticle.esql_execute(query)


    vector = chunk_handler.get_embeddings_by_ST([query])
    keys_results = ESIndexArticle.search().query(Match(ESIndexArticle.text, query))
    vec_results = ESIndexArticle.search().knn(field=ESIndexArticle.embedding, query_vector=vector[0][1], k=10, num_candidates=100)
    rank_keys = [hit.meta.id for hit in keys_results]
    rank_vecs = [hit.meta.id for hit in vec_results]
    fused_results = rrf_fusion([rank_keys, rank_vecs], k=60)
    logger.info(f"Fused results: {fused_results}")
    return rank_keys,rank_vecs,fused_results



    
if __name__ == "__main__":
    from utils.util_file_parse import FileParse,FileSource
    # text = FileParse = FileParse.parse_file(FileSource.from_path("static/docs/亿达科创差旅费管理制度.pdf"))
    # text = FileParse = FileParse.parse_file(FileSource.from_path("static/docs/机票预订操作流程图解.pdf"))
    # es = ESService(api_key=api_key)
    # index_name = "knowledge_base"
    # es.demo_create_index(index_name)
    # es.demo_save(index_name)
    # es.demo_query(index_name)
    # es.clear_index(index_name)

    # save(text)
    rank_keys, rank_vecs, fused_results = search("商务机票系统登录方法")
    pass
