import os
import time
from pathlib import Path
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import json
from collections import Counter
import truststore
truststore.inject_into_ssl()
import re
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

load_dotenv()
assert os.getenv("OPENAI_API_KEY")
assert os.getenv("QDRANT_URL")
assert os.getenv("QDRANT_API_KEY")

openai_client = OpenAI()
qdrant = QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ["QDRANT_API_KEY"])
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

EMBED_SMALL = "text-embedding-3-small"    # 1536 dims, $0.02 per 1M tokens
EMBED_LARGE = "text-embedding-3-large"    # 3072 dims, $0.13 per 1M tokens

# Load the corpus (15 docs) and 6 test queries with expected-winner annotations
BASE_DIR = Path(__file__).resolve().parent
CORPUS_PATH = BASE_DIR / "sample_docs" / "acme_docs.jsonl"
QUERIES_PATH = BASE_DIR / "sample_docs" / "acme_test_queries.jsonl"

queries = [json.loads(line) for line in QUERIES_PATH.read_text().splitlines() if line]
corpus  = [json.loads(line) for line in CORPUS_PATH.read_text().splitlines() if line]
COLLECTION = "wk09_day1_acme"
COLLECTION = "wk09_day2_acme"

def dense_search(query: str, k: int = 3):
    ## Embed the query
    q_vec = openai_client.embeddings.create(model=EMBED_SMALL, input=query).data[0].embedding
    
    ## search in qdrant using embedded query vector
    hits = qdrant.query_points(
        collection_name=COLLECTION,
        query=q_vec,
        limit=k
        ).points
    return [
        {"id": hit.payload.get("id"), "title": hit.payload.get("title"), "score": hit.score, "payload": hit.payload}
        for hit in hits
    ]
    
def simple_tokenize(text: str) -> list[str]:
    return re.findall(r'[a-z0-9][a-z0-9\-/_]*', text.lower())

def build_bm25_index(corpus: list[dict]):
    """Build a rank-bm25 BM25Okapi index over the corpus text field."""
    from rank_bm25 import BM25Okapi
    tokenized_corpus = [simple_tokenize(doc["text"] + " " + doc["title"]) for doc in corpus]
    return BM25Okapi(tokenized_corpus)

def bm25_search(index, corpus, query: str, k: int = 3) -> list[dict]:
    """Query BM25 index; return top-K."""
    tokens = simple_tokenize(query)
    scores = index.get_scores(tokens)
    ranked = sorted(zip(scores, corpus), key=lambda pair: pair[0], reverse=True)
    return [
        {"id": doc["id"], "title": doc["title"], "score": float(score), "doc": doc}
        for score, doc in ranked[:k]
    ]

def hybrid_retrieve(query: str, k_per_retriever: int = 10, k_final: int = 10) -> list[dict]:
    bm25_hits  = bm25_search(bm25, corpus, query, k=k_per_retriever)
    dense_hits = dense_search(query, k=k_per_retriever)
    dense_hits = [{"id": h["id"], "score": h["score"], "doc": h["payload"]} for h in dense_hits]
    return rrf_fuse([bm25_hits, dense_hits], k=60, top_n=k_final)
    
def rrf_fuse(ranked_lists: list[list[dict]], k: int = 60, top_n: int = 5) -> list[dict]:
    """Fuse multiple ranked lists via Reciprocal Rank Fusion.
    
    Each entry in ranked_lists is a list of dicts with an 'id' key.
    Returns the top-N fused results (with 'rrf_score' added).
    """
    scores = {}
    docs   = {}
    for ranked in ranked_lists:
        for rank, hit in enumerate(ranked, start=1):
            doc_id = hit["id"]
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
            if doc_id not in docs:
                docs[doc_id] = hit
    
    fused = sorted(scores.items(), key=lambda p: p[1], reverse=True)[:top_n]
    return [{**docs[doc_id], "rrf_score": score} for doc_id, score in fused]

def rerank(query: str, candidates: list[dict], top_k: int = 3) -> list[dict]:
    """Score each (query, candidate.text) pair; return top_k by rerank_score.
    
    candidates: list of dicts with 'doc' key containing full doc (must have 'text').
    Adds 'rerank_score' to each returned dict.
    """    
    pairs = [(query, hit["doc"]["text"]) for hit in candidates]
    scores = reranker.predict(pairs)
    scored = [{**hit, "rerank_score": float(s)} for hit, s in zip(candidates, scores)]
    scored.sort(key=lambda h: h["rerank_score"], reverse=True)
    return scored[:top_k]
        
if __name__ == "__main__":
    

    # try: 
    #     qdrant.delete_collection(COLLECTION)
    # except Exception: 
    #     pass

    # qdrant.create_collection(collection_name=COLLECTION,
    #                         vectors_config=VectorParams(size=1536, distance=Distance.COSINE))

    # # Embed + upsert
    # texts = [d["text"] for d in corpus]
    # vectors = [item.embedding for item in openai_client.embeddings.create(
    #     model="text-embedding-3-small", input=texts).data]
    # qdrant.upsert(collection_name=COLLECTION, points=[
    #     PointStruct(id=i, vector=v, payload=d) for i, (d, v) in enumerate(zip(corpus, vectors))
    # ])

    # Build BM25
    bm25 = build_bm25_index(corpus)

    # print(f"══ Full stack (hybrid → rerank) on all 6 queries (top-1) ══\n")
    # print(f"  {'Query':<50s}  {'Hybrid top-1':<18s}  {'Reranked top-1':<18s}  Verdict")
    # print(f"  {'-----':<50s}  {'------------':<18s}  {'--------------':<18s}  -------")

    # hybrid_correct   = 0
    # reranked_correct = 0

    # for tq in queries:
    #     hybrid_top10 = hybrid_retrieve(tq["q"], k_per_retriever=10, k_final=10)
    #     reranked_top3 = rerank(tq["q"], hybrid_top10, top_k=3)
        
    #     hybrid_top1 = hybrid_top10[0]["id"]
    #     rerank_top1 = reranked_top3[0]["id"]
        
    #     hybrid_ok   = hybrid_top1 == tq["expected_id"]
    #     rerank_ok   = rerank_top1 == tq["expected_id"]
    #     if hybrid_ok:   hybrid_correct += 1
    #     if rerank_ok:   reranked_correct += 1
        
    #     change = ""
    #     if not hybrid_ok and rerank_ok:  change = "  ← rerank FIXED"
    #     elif hybrid_ok and not rerank_ok: change = "  ← rerank BROKE (rare)"
        
    #     verdict = f"{'✓' if rerank_ok else '✗'} (expected {tq['expected_id']})"
    #     print(f"  {tq['q'][:50]:<50s}  {hybrid_top1:<18s}  {rerank_top1:<18s}  {verdict}{change}")

    # print()
    # print(f"══ Progression across all 3 stages ══")
    # print(f"  Hybrid retrieval (top-1):    {hybrid_correct}/{len(queries)}")
    # print(f"  + Cross-encoder rerank:      {reranked_correct}/{len(queries)}")
    # Time the full pipeline over 3 runs to get a stable-ish read
    test_query = "how do I export a dashboard to PDF"
    N_RUNS = 3

    stage_times = {"embed_query": [], "bm25": [], "dense": [], "rrf": [], "rerank": []}
    print("start")

    for _ in range(N_RUNS):
        # Stage: embed the query
        t0 = time.time()
        q_vec = openai_client.embeddings.create(
            model="text-embedding-3-small", input=[test_query]).data[0].embedding
        stage_times["embed_query"].append(time.time() - t0)
        
        # Stage: BM25 search
        t0 = time.time()
        bm25_hits = bm25_search(bm25, corpus, test_query, k=10)
        stage_times["bm25"].append(time.time() - t0)
        
        # Stage: Qdrant dense search
        t0 = time.time()
        dense_hits = qdrant.query_points(collection_name=COLLECTION, query=q_vec, limit=10).points
        dense_hits = [{"id": h.payload["id"], "score": h.score, "doc": h.payload} for h in dense_hits]
        stage_times["dense"].append(time.time() - t0)
        
        # Stage: RRF fusion
        t0 = time.time()
        fused = rrf_fuse([bm25_hits, dense_hits], k=60, top_n=10)
        stage_times["rrf"].append(time.time() - t0)
        
        # Stage: cross-encoder rerank
        t0 = time.time()
        _ = rerank(test_query, fused, top_k=3)
        stage_times["rerank"].append(time.time() - t0)

    print(f"══ Latency per stage (median of {N_RUNS} runs) ══\n")
    print(f"  {'Stage':<15s}  {'Time (ms)':>10s}  Notes")
    print(f"  {'-----':<15s}  {'---------':>10s}  -----")

    def median(lst): return sorted(lst)[len(lst)//2]

    notes = {
        "embed_query": "1 API call to OpenAI (network-bound)",
        "bm25":        "in-memory over 15 docs — trivial",
        "dense":       "1 API call to Qdrant (network-bound)",
        "rrf":         "pure Python arithmetic — free",
        "rerank":      "10 forward passes through CrossEncoder — CPU-bound",
    }

    total = 0
    for stage, times in stage_times.items():
        ms = median(times) * 1000
        total += ms
        print(f"  {stage:<15s}  {ms:>8.1f}    {notes[stage]}")

    print(f"  {'-'*15}  {'-'*9}")
    print(f"  {'TOTAL':<15s}  {total:>8.1f} ms")

    print()
    print("Key observation: reranker is usually the slowest stage. Its cost scales")
    print("LINEARLY with k_candidates. Doubling from 10 to 20 candidates ~doubles")
    print("rerank time. That's why we pick k_candidates=10 (not 100) as default.")