import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, HnswConfigDiff, PointStruct
from qdrant_client.models import ScalarQuantization, ScalarQuantizationConfig, ScalarType
from qdrant_client.models import ScalarQuantization, ScalarQuantizationConfig, ScalarType
# from Week7.day2_experiments import COLL_DOT, COLL_L2
# from Week7.day2_experiments import COLL_L2
from data import documents
import time

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

CORPUS_ANIMALS = documents

def embed_one(text: str, model: str = EMBED_SMALL) -> list[float]:
    resp = client.embeddings.create(model=model, input=[text])
    return resp.data[0].embedding

def embed_batch(texts: list[str], model: str = EMBED_SMALL) -> list[list[float]]:
    resp = client.embeddings.create(model=model, input=texts)
    return [item.embedding for item in resp.data]

def cosine(a, b):
    va, vb = np.array(a), np.array(b)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))

def linear_scan(query_vec, corpus, k=3):
    """Naive linear scan — compute similarity vs every doc, sort, take top-K."""
    scored = [(cosine(query_vec, doc["vector"]), doc) for doc in corpus]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:k]

def recreate_collection(name, size=1536, distance=Distance.COSINE, hnsw=None, quantization=False):
    """Delete-then-create so cells are re-runnable."""
    try:
        qdrant.delete_collection(name)
    except Exception:
        pass
    qdrant.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=size, distance=distance),
        quantization_config=ScalarQuantization(
            scalar=ScalarQuantizationConfig(
                type=ScalarType.INT8,
                quantile=0.99,
                always_ram=True,
            )
        ) if quantization else None,
        hnsw_config=hnsw,
    )

def upsert_animals(collection_name, CORPUS_ANIMALS):
    """Push the 10 animals into a collection."""
    points = [
        PointStruct(
            id=idx,
            vector=doc["vector"],
            payload={"animal_id": doc["id"], "category": doc["category"], "text": doc["text"]},
        )
        for idx, doc in enumerate(CORPUS_ANIMALS)
    ]
    qdrant.upsert(collection_name=collection_name, points=points)

def dot(a: list[float], b: list[float]) -> float:
    """Dot product — measures angle + magnitude. Higher = more similar."""
    return float(np.dot(np.array(a), np.array(b)))

def l2(a: list[float], b: list[float]) -> float:
    """L2 distance — measures straight-line distance. Lower = more similar."""
    return float(np.linalg.norm(np.array(a) - np.array(b)))

texts = [d["text"] for d in documents]
vectors = embed_batch(texts)
for doc, vec in zip(documents, vectors):
        doc["vector"] = vec
        
SYSTEM = (
    "You are a helpful assistant. Answer using ONLY the provided context. "
    "If the context does not contain the answer, say so plainly. Cite the "
    "animal id in square brackets after any fact you use.")

        
def ask_qdrant_rag(question: str, collection: str, k: int = 3) -> dict:
    """Full mini-RAG: embed → Qdrant retrieve → prompt → generate."""
    # 1. Embed the query
    q_vec = embed_one(question)
    
    # 2. Retrieve top-K from Qdrant
    hits = qdrant.query_points(
        collection_name=collection,
        query=q_vec,
        limit=k,
    ).points
    
    # 3. Build the prompt with retrieved chunks
    context = "\n\n".join(
        f"[{h.payload['animal_id']}]\n{h.payload['text']}"
        for h in hits
    )
    
    # 4. Generate
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user",   "content":
                f"Context:\n{context}\n\n---\n\nQuestion: {question}"},
        ],
    )
    
    return {
        "question": question,
        "answer":   resp.choices[0].message.content,
        "sources":  [h.payload["animal_id"] for h in hits],
    }

if __name__ == "__main__":
    
    COLL_HNSW_DEFAULT = "wk07_day2_hnsw_default"
    COLL_HNSW_TUNED = "wk07_day2_hnsw_tuned"
    COLL_QUANT = "wk07_day2_quantized"
    COLL_COSINE = "wk07_day2_metric_cosine"
    COLL_DOT    = "wk07_day2_metric_dot"
    COLL_L2     = "wk07_day2_metric_l2"    
    
#     TEST_QUESTIONS = [
#     {"q": "Which animals live in the ocean?",              "expected_categories": ["fish"]},
#     {"q": "What insects live in social colonies?",         "expected_categories": ["insect"]},
#     {"q": "What animals have keen eyesight for hunting?",  "expected_categories": ["bird"]},
#     {"q": "Which animals are kept as pets?",               "expected_categories": ["mammal", "reptile"]},
#     {"q": "How do reptiles kill their prey?",              "expected_categories": ["reptile"]},
# ]

#     for tq in TEST_QUESTIONS:
#         result = ask_qdrant_rag(tq["q"], COLL_COSINE, k=3)
#         print(f"── {tq['q']}")
#         print(f"   expected categories: {tq['expected_categories']}")
#         print(f"   sources retrieved:   {result['sources']}")
#         print(f"   answer: {result['answer']}")
#         print()
    for coll in [COLL_HNSW_DEFAULT, COLL_HNSW_TUNED, COLL_QUANT,
             COLL_COSINE, COLL_DOT, COLL_L2]:
        try:
            qdrant.delete_collection(coll)
            print(f"  deleted {coll}")
        except Exception as e:
            print(f"  skip {coll}: {e}")

    print("\nDay 1's animals collection (wk07_day1_animals) is preserved.")
    print("Delete manually if you don't want it.")
    
    print(qdrant.get_collections())
    