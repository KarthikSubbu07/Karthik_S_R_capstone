import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, HnswConfigDiff, PointStruct
from qdrant_client.models import ScalarQuantization, ScalarQuantizationConfig, ScalarType
from qdrant_client.models import ScalarQuantization, ScalarQuantizationConfig, ScalarType
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

if __name__ == "__main__":
    ### Check existing collection in Qdrant
    # collections = qdrant.get_collections().collections
    # for col in collections:
    #     print(f"Collection name: {col.name}")
    
    ##TESt Linear scan, checking time it takes to validate every vector in the store
    # query = "Which animals live in the ocean?"
    # q_vec = embed_one(query)

    # # Time the linear scan on our 10-doc corpus
    
    # t0 = time.time()
    # hits = linear_scan(q_vec, documents, k=3)
    # dt = time.time() - t0

    # print(f"Q: {query!r}")
    # print(f"Linear scan over {len(documents)} docs took {dt*1000:.2f} ms\n")
    # for score, doc in hits:
    #     print(f"  {score:.3f}  {doc['id']:8s}  ({doc['category']})")
    
    ##Recreate collection
    COLL_HNSW_DEFAULT = "wk07_day2_hnsw_default"
    # recreate_collection(COLL_HNSW_DEFAULT)  # HNSW is Qdrant's default; no config = defaults
    # upsert_animals(COLL_HNSW_DEFAULT, documents)
    
    # info = qdrant.get_collection(COLL_HNSW_DEFAULT)
    # hnsw = info.config.hnsw_config
    # print(f"Collection {COLL_HNSW_DEFAULT!r} — HNSW default config:")
    # print(f"  m:               {hnsw.m}          (graph connectivity — higher = more edges per node)")
    # print(f"  ef_construct:    {hnsw.ef_construct}         (build-time search depth — higher = better recall, slower build)")
    # print(f"  full_scan_threshold: {hnsw.full_scan_threshold}   (below this many points, use linear scan)")
    
    COLL_HNSW_TUNED = "wk07_day2_hnsw_tuned"
    # recreate_collection(
    #     COLL_HNSW_TUNED,
    #     hnsw=HnswConfigDiff(m=32, ef_construct=200),  # 2× default on both
    # )
    # upsert_animals(COLL_HNSW_TUNED, documents)

    # info = qdrant.get_collection(COLL_HNSW_TUNED)
    # hnsw = info.config.hnsw_config
    # print(f"Collection {COLL_HNSW_TUNED!r} — HNSW tuned config:")
    # print(f"  m:            {hnsw.m}  (was 16, now 32)")
    # print(f"  ef_construct: {hnsw.ef_construct}  (was 100, now 200)")
    # print()
    # print("Effect at production scale:")
    # print("  - Better recall (misses fewer true top-K on approximate queries)")
    # print("  - More memory (each node has 2× the edges to store)")
    # print("  - Slower build time (index construction does 2× more work)")
    # print("  - Query speed roughly the same (HNSW query cost is O(log n × ef))")
    
    COLL_QUANT = "wk07_day2_quantized"
    # recreate_collection(COLL_QUANT, quantization=True)
    # upsert_animals(COLL_QUANT, documents)
    
    
    # info = qdrant.get_collection(COLL_QUANT)
    # print(f"Collection {COLL_QUANT!r} created with scalar quantization.")
    # print(f"  Storage per vector before:  1536 × 4 bytes = 6144 bytes")
    # print(f"  Storage per vector after:   1536 × 1 byte  = 1536 bytes  (4× smaller)")
    # print()
    # print("On our 10-animal corpus this saves ~45 KB — trivial.")
    # print("On 10M vectors, this saves 45 GB. That's when quantization pays off.")
        
    COLL_COSINE = "wk07_day2_metric_cosine"
    COLL_DOT    = "wk07_day2_metric_dot"
    COLL_L2     = "wk07_day2_metric_l2"

    # recreate_collection(COLL_COSINE, distance=Distance.COSINE)
    # recreate_collection(COLL_DOT,    distance=Distance.DOT)
    # recreate_collection(COLL_L2,     distance=Distance.EUCLID)

    # upsert_animals(COLL_COSINE, documents)
    # upsert_animals(COLL_DOT, documents)
    # upsert_animals(COLL_L2, documents)
    
    # query = "What animals hunt from the sky?"
    # q_vec = embed_one(query)

    # print(f"Q: {query!r}\n")
    # for coll, label in [(COLL_COSINE, "COSINE"),
    #                     (COLL_DOT,    "DOT PRODUCT"),
    #                     (COLL_L2,     "L2 (Euclidean, lower = closer)")]:
    #     hits = qdrant.query_points(collection_name=coll, query=q_vec, limit=3).points
    #     print(f"  {label}:")
    #     for h in hits:
    #         p = h.payload
    #         print(f"    {h.score:>7.3f}  {p['animal_id']:8s} ({p['category']})")
    #     print()
    
    vec_cat   = next(d['vector'] for d in CORPUS_ANIMALS if d['id'] == 'cat')
    # vec_dog   = next(d['vector'] for d in CORPUS_ANIMALS if d['id'] == 'dog')
    # vec_bee   = next(d['vector'] for d in CORPUS_ANIMALS if d['id'] == 'bee')

    # pairs = [("cat", "dog", vec_cat, vec_dog, "similar (both mammals)"),
    #         ("cat", "bee", vec_cat, vec_bee, "different (mammal vs insect)")]

    # print(f"  {'Pair':15s}  {'cosine':>8s}  {'dot':>8s}  {'l2':>8s}   Interpretation")
    # print(f"  {'----':15s}  {'------':>8s}  {'---':>8s}  {'--':>8s}   {'-'*30}")
    # for a, b, va, vb, note in pairs:
    #     c = cosine(va, vb)
    #     d = dot(va, vb)
    #     l = l2(va, vb)
    #     print(f"  {a:<5s} vs {b:6s}  {c:>8.3f}  {d:>8.3f}  {l:>8.3f}   {note}")

    # print()
    # print("Note: for OpenAI embeddings (unit-length), cosine ≈ dot product,")
    # print("and L2 = sqrt(2 - 2*cosine).")
    # print("Cosine higher = closer.  Dot higher = closer.  L2 lower = closer.")

# Simulate non-normalised custom embeddings: scale some vectors up 3x for no reason
    scaled_docs = []
    for d in CORPUS_ANIMALS:
        scale = 3.0 if d['id'] in ["salmon", "ant"] else 1.0   # arbitrarily scaled
        vec = [v * scale for v in d['vector']]
        scaled_docs.append({**d, "vector": vec, "scale": scale})

    # Query 'ocean animals' — the honest cosine ranking should put salmon and shark on top.
    query = "Which animals live in the ocean?"
    q_vec = embed_one(query)

    # Rank by cosine (correct — scale-invariant)
    cos_scored = [(cosine(q_vec, d['vector']), d) for d in scaled_docs]
    cos_scored.sort(key=lambda p: p[0], reverse=True)

    # Rank by dot product (WRONG when vectors aren't normalised — magnitude wins)
    dot_scored = [(dot(q_vec, d['vector']), d) for d in scaled_docs]
    dot_scored.sort(key=lambda p: p[0], reverse=True)

    print(f"Q: {query!r}\n")
    print("  COSINE ranking (correct):")
    for s, d in cos_scored[:5]:
        marker = "  ← scaled 3x" if d['scale'] > 1 else ""
        print(f"    {s:>7.3f}  {d['id']:8s} ({d['category']:7s}){marker}")

    print("\n  DOT PRODUCT ranking (buggy — magnitude wins over meaning):")
    for s, d in dot_scored[:5]:
        marker = "  ← scaled 3x" if d['scale'] > 1 else ""
        print(f"    {s:>7.3f}  {d['id']:8s} ({d['category']:7s}){marker}")


    # query = "Which animals live in the ocean?"
    # q_vec = embed_one(query)

    # for coll in [COLL_HNSW_DEFAULT, COLL_HNSW_TUNED, COLL_QUANT]:
    #     hits = qdrant.query_points(collection_name=coll, query=q_vec, limit=3).points
    #     print(f"  {coll}:")
    #     for h in hits:
    #         p = h.payload
    #         print(f"    {h.score:.3f}  {p['animal_id']:8s} ({p['category']})")
    #     print()
    
#     queries = [
#     "Which animals live in the ocean?",
#     "What insects live in social colonies?",
#     "What animals hunt from the sky?",
#     "Which animals are kept as pets?",
# ]

# for query in queries:
#     print("Start")
#     q_vec = embed_one(query)
#     print("done")
#     results = qdrant.query_points(
#         collection_name=COLL_HNSW_DEFAULT,
#         query=q_vec,
#         limit=3,
#     ).points
    
#     print(f"Q: {query!r}")
#     for i, hit in enumerate(results, 1):
#         p = hit.payload
#         print(f"  [{i}] score={hit.score:.3f}  {p['animal_id']:8s} ({p['category']})")
#     print()