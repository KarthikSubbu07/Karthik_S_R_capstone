import os
import sys
from pathlib import Path
import time
from flask.cli import load_dotenv

# Add cwd to path so we can import wk10_pipeline
sys.path.insert(0, str(Path.cwd()))

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    FieldCondition, Filter, MatchValue,
    IsNullCondition, IsEmptyCondition, PayloadField,
    PayloadSchemaType,
)
import truststore
truststore.inject_into_ssl()

from wk10_pipeline import (
    load_acme_corpus, load_test_queries,
    make_live_filter, make_broken_filter,
    cache_init, cache_clear, cache_put, cache_lookup,
    build_rag_prompt, count_tokens, estimate_cost_usd,
)

load_dotenv()
assert os.getenv("OPENAI_API_KEY")
assert os.getenv("QDRANT_URL")
assert os.getenv("QDRANT_API_KEY")

corpus  = load_acme_corpus()
queries = load_test_queries()
openai_client = OpenAI()
qdrant = QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ["QDRANT_API_KEY"])
COLLECTION = "wk10_day2_acme"

from wk10_pipeline import (
    load_acme_corpus, load_test_queries,
    build_rag_prompt, count_tokens,
    cache_init, cache_put, cache_lookup, cache_clear, cache_key,
    estimate_cost_usd, PRICING,
)

# Recreate collection
try:    qdrant.delete_collection(COLLECTION)
except: pass
qdrant.create_collection(COLLECTION,
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE))

for field, schema in [
    ("source",     PayloadSchemaType.KEYWORD),
    ("deleted_at", PayloadSchemaType.FLOAT),
]:
    try:
        qdrant.create_payload_index(
            collection_name=COLLECTION,
            field_name=field,
            field_schema=schema,
            wait=True,
        )
    except Exception:
        pass  # already exists — safe
print(f"✓ Payload indexes ensured: source (keyword), deleted_at (float)")

    
def embed_texts(texts):
    return [item.embedding for item in openai_client.embeddings.create(
        model="text-embedding-3-small", input=texts).data]

# Ingest — NO deleted_at field set (this is critical for Cell 4's bug)
vectors = embed_texts([d["text"] for d in corpus])
points = [
    PointStruct(
        id=i,
        vector=vec,
        payload={**doc, "source": doc["id"], "ingested_at": time.time()},
        # NOTE: deliberately NO deleted_at field. Matches what naive
        # ingestion does — the field only appears when tombstoned.
    )
    for i, (doc, vec) in enumerate(zip(corpus, vectors))
]
qdrant.upsert(COLLECTION, points=points, wait=True)
print(f"✓ Ingested {len(points)} chunks into {COLLECTION!r} (no deleted_at set)")

def tombstone_source(source_name: str) -> int:
    """Mark all live chunks from source as tombstoned. USES IsEmptyCondition.
    
    IsEmpty matches whether deleted_at is absent, null, or empty list —
    all three represent "not yet tombstoned" in practice.
    """
    flt = Filter(must=[
        FieldCondition(key="source", match=MatchValue(value=source_name)),
        IsEmptyCondition(is_empty=PayloadField(key="deleted_at")),
    ])
    pre_count = qdrant.count(COLLECTION, count_filter=flt, exact=True).count
    
    qdrant.set_payload(
        collection_name=COLLECTION,
        payload={"deleted_at": time.time()},
        points=flt,
        wait=True,
    )
    return pre_count

print("══ Attempt 2: tombstone using IsEmptyCondition ══\n")
n = tombstone_source("feat_dashboards")
print(f"✓ Tombstoned {n} chunk(s) from source=feat_dashboards\n")

# Verify — the OLD point (id=0) should now have deleted_at set;
# the NEW point (id=100) should NOT (we inserted it after the tombstone would have run).
# Actually wait — we inserted id=100 in Cell 2 BEFORE running tombstone. So id=100 was
# also live when tombstone ran. Let's check what actually happened:
print("Current state of feat_dashboards chunks:")
scroll_result, _ = qdrant.scroll(
    COLLECTION,
    scroll_filter=Filter(must=[FieldCondition(key="source", match=MatchValue(value="feat_dashboards"))]),
    limit=10,
    with_payload=True,
)
for p in scroll_result:
    deleted = p.payload.get("deleted_at")
    status = f"tombstoned at {deleted:.0f}" if deleted else "LIVE"
    print(f"  id={p.id}  status={status}  text={p.payload['text'][:50]}...")
    
def dense_retrieve_v10(query: str, k: int = 5, include_deleted: bool = False):
    """Retrieval with tombstone filter applied by default.
    
    include_deleted=True is the audit escape hatch — set only when re-running
    historical evaluations that need the KB as it existed then.
    """
    q_vec = embed_texts([query])[0]
    query_filter = None if include_deleted else make_live_filter()
    hits = qdrant.query_points(
        COLLECTION, query=q_vec, limit=k, query_filter=query_filter,
    ).points
    return [{"id": h.id, "score": h.score, "doc": h.payload} for h in hits]

# query = "how do I export a dashboard to PDF"

# print(f"Query: {query!r}\n")

# print("WITHOUT tombstone filter (include_deleted=True):")
# for h in dense_retrieve_v10(query, k=3, include_deleted=True):
#     dead = h["doc"].get("deleted_at") is not None
#     mark = " [TOMBSTONED]" if dead else ""
#     print(f"  id={h['id']}  score={h['score']:.4f}  {h['doc'].get('source', '?')}{mark}")

# print("\nWITH tombstone filter (default — include_deleted=False):")
# for h in dense_retrieve_v10(query, k=3):
#     print(f"  id={h['id']}  score={h['score']:.4f}  {h['doc'].get('source', '?')}")

# print("\nExpected: the second list excludes both tombstoned dashboards chunks.")
# print("Live retrieval returns only currently-live docs.")