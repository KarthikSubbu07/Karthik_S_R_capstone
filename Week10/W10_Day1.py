import os
import sys
from pathlib import Path
from flask.cli import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import truststore
truststore.inject_into_ssl()

load_dotenv()
assert os.getenv("OPENAI_API_KEY")
assert os.getenv("QDRANT_URL")
assert os.getenv("QDRANT_API_KEY")

openai_client = OpenAI()
qdrant = QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ["QDRANT_API_KEY"])

# Add cwd to path so we can import wk10_pipeline
sys.path.insert(0, str(Path.cwd()))

from wk10_pipeline import (
    load_acme_corpus, load_test_queries,
    build_rag_prompt, count_tokens,
    cache_init, cache_put, cache_lookup, cache_clear, cache_key,
    estimate_cost_usd, PRICING,
)

corpus  = load_acme_corpus()
queries = load_test_queries()
print(f"✓ Loaded {len(corpus)} docs and {len(queries)} test queries (reused from W9)")

COLLECTION = "wk10_day1_acme"

# Recreate collection + embed corpus
try:    
    qdrant.delete_collection(COLLECTION)
except: 
    pass
qdrant.create_collection(COLLECTION,
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE))

texts = [d["text"] for d in corpus]
vectors = [item.embedding for item in openai_client.embeddings.create(
    model="text-embedding-3-small", input=texts).data]
qdrant.upsert(COLLECTION, points=[
    PointStruct(id=i, vector=v, payload=d) for i, (d, v) in enumerate(zip(corpus, vectors))
])
print(f"✓ Ingested {len(corpus)} chunks into {COLLECTION!r}")

def dense_search(q, k=5):
    q_vec = openai_client.embeddings.create(
        model="text-embedding-3-small", input=[q]).data[0].embedding
    hits = qdrant.query_points(COLLECTION, query=q_vec, limit=k).points
    return [{"id": h.payload["id"], "score": h.score, "doc": h.payload} for h in hits]

# Precision@k = 1 if expected_id in top-k retrieved
# Recall@k on this corpus = same (single expected doc per query) — but on
# multi-answer questions they diverge. See the discussion after this cell.
def p_at_k(retrieved_ids, expected_id, k):
    return 1.0 if expected_id in retrieved_ids[:k] else 0.0

print(f"\n══ Precision@k for k=3 vs k=5 ══\n")
print(f"  {'Query':<50s}  {'P@3':>5s}  {'P@5':>5s}  {'tokens saved at k=3'}")

p3_sum, p5_sum = 0.0, 0.0
for tq in queries:
    top5 = dense_search(tq["q"], k=5)
    ids = [h["id"] for h in top5]
    p3 = p_at_k(ids, tq["expected_id"], 3)
    p5 = p_at_k(ids, tq["expected_id"], 5)
    p3_sum += p3; p5_sum += p5
    
    # Estimate tokens saved by dropping positions 4,5
    saved = sum(count_tokens(h["doc"]["text"]) for h in top5[3:])
    print(f"  {tq['q'][:50]:<50s}  {p3:>5.2f}  {p5:>5.2f}  ~{saved} tokens")

n = len(queries)
print(f"\n  Precision@3 = {p3_sum/n:.2f}   Precision@5 = {p5_sum/n:.2f}")
print(f"\n  Decision: safe to cut k=5 → k=3? — {'YES' if p3_sum == p5_sum else 'CHECK'}")