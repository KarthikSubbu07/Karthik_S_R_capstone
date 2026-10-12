import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from data import documents

load_dotenv()
assert os.getenv("OPENAI_API_KEY")
assert os.getenv("QDRANT_URL")
assert os.getenv("QDRANT_API_KEY")

import truststore
truststore.inject_into_ssl()

client = OpenAI()
qdrant = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.environ["QDRANT_API_KEY"],
)

COLLECTION_NAME = "wk07_day1_animals"
EMBED_SMALL = "text-embedding-3-small"    # 1536 dims, $0.02 per 1M tokens
EMBED_LARGE = "text-embedding-3-large"    # 3072 dims, $0.13 per 1M tokens

def embed_one(text: str, model: str = EMBED_SMALL) -> list[float]:
    resp = client.embeddings.create(model=model, input=[text])
    return resp.data[0].embedding

# def embed_batch(texts, model=EMBED_SMALL):
#     resp = client.embeddings.create(model=model, input=texts)
#     return [item.embedding for item in resp.data]

def cosine(a, b):
    va, vb = np.array(a), np.array(b)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))

if __name__ == "__main__":
    queries = [
    "Which animals live in the ocean?",
    "What insects live in social colonies?",
    "What animals hunt from the sky?",
    "Which animals are kept as pets?",
]

for query in queries:
    print("Start")
    q_vec = embed_one(query)
    print("done")
    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=q_vec,
        limit=3,
    ).points
    
    print(f"Q: {query!r}")
    for i, hit in enumerate(results, 1):
        p = hit.payload
        print(f"  [{i}] score={hit.score:.3f}  {p['animal_id']:8s} ({p['category']})")
    print()