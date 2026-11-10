import os
import sys
from pathlib import Path
import time
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

# corpus  = load_acme_corpus()
# queries = load_test_queries()
# print(f"✓ Loaded {len(corpus)} docs and {len(queries)} test queries (reused from W9)")

COLLECTION = "wk10_day1_acme"

# Initialise the cache database
CACHE_DB = "wk10_day1_cache.db"
# Clean slate for the demo
if os.path.exists(CACHE_DB):
    os.remove(CACHE_DB)

cache = cache_init(CACHE_DB)
print(f"✓ Cache initialised: {CACHE_DB}")

def dense_search(q, k=5):
    q_vec = openai_client.embeddings.create(
        model="text-embedding-3-small", input=[q]).data[0].embedding
    hits = qdrant.query_points(COLLECTION, query=q_vec, limit=k).points
    return [{"id": h.payload["id"], "score": h.score, "doc": h.payload} for h in hits]

def embed_query(q: str) -> list[float]:
    return openai_client.embeddings.create(
        model="text-embedding-3-small", input=[q]).data[0].embedding

def rag_answer(q: str) -> tuple[str, dict]:
    """Full RAG pipeline: retrieve → build prompt → LLM.
    Returns (answer, meta) where meta includes token counts."""
    top3 = dense_search(q, k=3)
    prompt, counts = build_rag_prompt(q, top3)
    resp = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = resp.choices[0].message.content
    meta = {
        "n_input_tokens":  resp.usage.prompt_tokens,
        "n_output_tokens": resp.usage.completion_tokens,
        "n_cached_input_tokens": getattr(resp.usage, 'prompt_tokens_details', None)
                                  and resp.usage.prompt_tokens_details.cached_tokens or 0,
        "n_embed_tokens":  len(q.split()),  # rough
    }
    return answer, meta

def cached_rag_answer(q: str, threshold: float = 0.95) -> tuple[str, dict]:
    """Cache-first RAG. Miss → full pipeline + store. Hit → return cached."""
    q_vec = embed_query(q)
    hit = cache_lookup(cache, q_vec, threshold=threshold)
    if hit:
        return hit["answer"], {
            "cache_hit": True,
            "similarity": hit["similarity"],
            "matched": hit["matched_question"],
        }
    answer, meta = rag_answer(q)
    cache_put(cache, q, q_vec, answer)
    meta["cache_hit"] = False
    return answer, meta


print("✓ Cache-first RAG function ready")
print("\nSanity check — first call MISSES (empty cache), second call HITS:")

q = "what is error code AC-1042"
print(f"\n  Q: {q!r}")

t0 = time.time()
ans1, meta1 = cached_rag_answer(q)
print(f"  Call 1: hit={meta1['cache_hit']}, {(time.time()-t0)*1000:.0f}ms → {ans1[:80]}...")

t0 = time.time()
ans2, meta2 = cached_rag_answer(q)
print(f"  Call 2: hit={meta2['cache_hit']}, sim={meta2.get('similarity'):.4f}, {(time.time()-t0)*1000:.0f}ms")

### Cache fuine tuning

# ── Part 1: three paraphrases at three thresholds ──
# Cache is already primed with "what is error code AC-1042" from Cell 5.

paraphrases = [
    "what is error code AC-1042",       # original (from Cell 5) — expect exact match
    "AC-1042 error meaning",             # shorter paraphrase
    "tell me about the AC-1042 error",   # different phrasing
    "what does AC-1042 mean",            # another rephrasing
]
thresholds = [0.85, 0.95, 0.98]

print(f"══ Part 1: paraphrase hit rate at 3 thresholds ══\n")
print(f"  {'Query':<45s} | {'sim':>6s} | " + " | ".join(f"t={t}" for t in thresholds))
print(f"  {'-'*45} + {'-'*6} + " + " + ".join("-----" for _ in thresholds))

for p in paraphrases:
    p_vec = embed_query(p)
    # Get the raw similarity independent of threshold
    hit_any = cache_lookup(cache, p_vec, threshold=-1.0)  # -1.0 = always return match
    sim = hit_any["similarity"] if hit_any else 0.0
    
    hits_at = []
    for t in thresholds:
        h = "HIT" if sim >= t else "miss"
        hits_at.append(h)
    print(f"  {p[:45]:<45s} | {sim:>6.4f} | " + " | ".join(f"{h:>5s}" for h in hits_at))

print("\nExpected: all paraphrases hit at 0.85 and 0.95; some miss at 0.98")

print("***********")
distinct_q = "what is error code AC-4408"

q_vec = embed_query(distinct_q)
hit_at_min = cache_lookup(cache, q_vec, threshold=-1.0)
sim = hit_at_min["similarity"] if hit_at_min else 0.0

print(f"══ Part 2: false-hit demonstration ══\n")
print(f"  New question: {distinct_q!r}")
print(f"  Cached question that matches best: {hit_at_min['matched_question']!r}")
print(f"  Cosine similarity: {sim:.4f}\n")

for t in [0.85, 0.90, 0.95]:
    triggered = sim >= t
    verdict = 'CACHE HIT — returns WRONG answer (about AC-1042)' if triggered else 'cache miss — falls through to RAG (correct)'
    warning = ' ⚠' if triggered else ''
    print(f"  Threshold {t}: {verdict}{warning}")

# What's the actual cached answer we'd wrongly return at t=0.85?
print(f"\n  If we served the cached answer for {distinct_q!r} at t=0.85:")
print(f"  → {hit_at_min['answer'][:120]}...")
print(f"\n  User would get a plausible-looking answer to the WRONG question.")
print(f"  Silent quality regression. This is why deck slide 12 says")
print(f"  \"never ship < 0.95 without manual review of 20+ cache hits.\"")