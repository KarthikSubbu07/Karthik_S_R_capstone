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

corpus  = load_acme_corpus()
queries = load_test_queries()
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

# # Run the SAME prompt structure twice, inspect cached_tokens field.
# # We use a longer question to push the prompt past 1024 tokens.
# test_q = ("I need a detailed explanation of what causes error AC-1042 in the "
#           "Acme Analytics Platform, what the resolution steps are, whether it "
#           "relates to Snowflake connections, and what the default timeout is.")

# print(f"══ Prompt cache demonstration ══\n")

# # Bypass the semantic cache — call RAG directly twice
# for run in [1, 2]:
#     t0 = time.time()
#     _, meta = rag_answer(test_q)
#     elapsed_ms = (time.time() - t0) * 1000
#     cached = meta['n_cached_input_tokens']
#     total_input = meta['n_input_tokens']
#     pct_cached = 100 * cached / total_input if total_input else 0
#     print(f"  Run {run}: input={total_input:4d} tokens, cached={cached:4d} ({pct_cached:.0f}%), {elapsed_ms:.0f}ms")

# print(f"\nExpected pattern:")
# print(f"  Run 1: cached=0 (cold — nothing in provider cache yet)")
# print(f"  Run 2: cached=~950 (prefix matched; discounted billing)")
# print(f"\nIf Run 2 shows cached=0 too, either:")
# print(f"  • Prompt is <1024 tokens (below OpenAI's threshold)")
# print(f"  • Prompt prefix differs somehow (check that system prompt is byte-identical)")
# print(f"  • Model doesn't support prompt cache (gpt-4o-mini does; verify current docs)")

# Clear the cache so we're truly cold
cache_clear(cache)
print(f"✓ Cache cleared for cold pass\n")

def run_pass(label):
    total_cost, latencies = 0.0, []
    n_hits, n_misses = 0, 0
    for tq in queries:
        t0 = time.time()
        ans, meta = cached_rag_answer(tq["q"])
        elapsed_ms = (time.time() - t0) * 1000
        latencies.append(elapsed_ms)
        if meta["cache_hit"]:
            n_hits += 1
            # Cache hit cost = only the query-embedding call
            total_cost += estimate_cost_usd(0, 0, 0, n_embed_tokens=count_tokens(tq["q"]))
        else:
            n_misses += 1
            total_cost += estimate_cost_usd(
                n_input_tokens=meta["n_input_tokens"],
                n_output_tokens=meta["n_output_tokens"],
                n_cached_input_tokens=meta["n_cached_input_tokens"],
                n_embed_tokens=count_tokens(tq["q"]),
            )
    p50 = sorted(latencies)[len(latencies)//2]
    return {"label": label, "cost": total_cost, "p50_ms": p50,
            "hits": n_hits, "misses": n_misses, "total": len(queries)}

cold = run_pass("cold")
warm = run_pass("warm")

print(f"══ Cold vs Warm across {len(queries)} queries ══\n")
print(f"  {'Pass':<8s}  {'hits':>5s}  {'misses':>7s}  {'p50 ms':>8s}  {'cost':>10s}")
print(f"  {'----':<8s}  {'----':>5s}  {'------':>7s}  {'------':>8s}  {'----':>10s}")
print(f"  {cold['label']:<8s}  {cold['hits']:>5d}  {cold['misses']:>7d}  {cold['p50_ms']:>8.0f}  ${cold['cost']:>9.5f}")
print(f"  {warm['label']:<8s}  {warm['hits']:>5d}  {warm['misses']:>7d}  {warm['p50_ms']:>8.0f}  ${warm['cost']:>9.5f}")

if cold['cost'] > 0:
    cost_saved_pct = 100 * (cold['cost'] - warm['cost']) / cold['cost']
    latency_saved_pct = 100 * (cold['p50_ms'] - warm['p50_ms']) / cold['p50_ms']
    print(f"\n  Warm-pass cost saved:    {cost_saved_pct:.1f}%")
    print(f"  Warm-pass latency saved: {latency_saved_pct:.1f}%")