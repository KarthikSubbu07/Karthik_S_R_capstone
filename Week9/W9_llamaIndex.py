# llamaindex_sketch = '''
# ── LlamaIndex equivalent of our hybrid+rerank pipeline (~20 lines) ──
# NOT RUN — sketch only. Would require: pip install llama-index

import truststore
truststore.inject_into_ssl()

import os
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.postprocessor import SentenceTransformerRerank
import bm25s
# from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.qdrant import QdrantVectorStore
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import CrossEncoder

load_dotenv()
openai_client = OpenAI()
qdrant = QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ["QDRANT_API_KEY"])
# reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# 1. Set up dense retriever (Qdrant)
vector_store = QdrantVectorStore(client=qdrant, collection_name="capstone_chunks_v2")
index = VectorStoreIndex.from_vector_store(vector_store)
dense_retriever = index.as_retriever(similarity_top_k=10)

# 2. Set up BM25 retriever
# bm25_retriever = BM25Retriever.from_defaults(docstore=index.docstore, similarity_top_k=10)

# # 3. Fuse them via LlamaIndex\'s built-in RRF
# hybrid_retriever = QueryFusionRetriever(
#     [dense_retriever, bm25_retriever],
#     similarity_top_k=10,
#     mode="reciprocal_rerank",  # RRF
# )

# # 4. Cross-encoder reranker as a postprocessor
# reranker = SentenceTransformerRerank(model="cross-encoder/ms-marco-MiniLM-L-6-v2", top_n=3)

# # 5. Use it
# candidates = hybrid_retriever.retrieve("how do I export a dashboard")
# final = reranker.postprocess_nodes(candidates, query_str="how do I export a dashboard")
# for node in final:
#     print(node.text[:100], node.score)
# '''

# print(llamaindex_sketch)
# print("\nWhat it does: exactly what we built in Day 1 + Day 2 Cells 1-5.")
# print("What it hides: RRF math, tokenization, cross-encoder wrapping.")
# print("What you gain: composition. Swap dense_retriever, bm25_retriever, or reranker")
# print("               freely without touching the fusion or postprocessing.")
# print("What you lose: visibility into the wire format between stages.")