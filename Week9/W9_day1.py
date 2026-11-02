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

load_dotenv()
assert os.getenv("OPENAI_API_KEY")
assert os.getenv("QDRANT_URL")
assert os.getenv("QDRANT_API_KEY")

openai_client = OpenAI()
qdrant = QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ["QDRANT_API_KEY"])

EMBED_SMALL = "text-embedding-3-small"    # 1536 dims, $0.02 per 1M tokens
EMBED_LARGE = "text-embedding-3-large"    # 3072 dims, $0.13 per 1M tokens

# Load the corpus (15 docs) and 6 test queries with expected-winner annotations
BASE_DIR = Path(__file__).resolve().parent
CORPUS_PATH = BASE_DIR / "sample_docs" / "acme_docs.jsonl"
QUERIES_PATH = BASE_DIR / "sample_docs" / "acme_test_queries.jsonl"


queries = [json.loads(line) for line in QUERIES_PATH.read_text().splitlines() if line]

COLLECTION = "wk09_day1_acme"

## Block 1: Setup Qdrant and upsert embeddings for the corpus

corpus  = [json.loads(line) for line in CORPUS_PATH.read_text().splitlines() if line]
# Recreate — makes this cell re-runnable
# try:
#     qdrant.delete_collection(COLLECTION)
# except Exception:
#     pass

# qdrant.create_collection(
#     collection_name=COLLECTION,
#     vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
# )

# # Embed all 15 docs in one API call
# print("Embedding 15 Acme docs...")
# texts = [d["text"] for d in corpus]
# resp = openai_client.embeddings.create(model="text-embedding-3-small", input=texts)
# vectors = [item.embedding for item in resp.data]

# # Upsert
# points = [
#     PointStruct(id=idx, vector=vec, payload=doc)
#     for idx, (doc, vec) in enumerate(zip(corpus, vectors))
# ]
# qdrant.upsert(collection_name=COLLECTION, points=points)
# print(f"Upserted {len(points)} vectors into {COLLECTION!r}.")

### End of Block 1

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

def bm25_search(query: str, k: int = 3) -> list[dict]:
    """Query BM25 index; return top-K."""
    tokens = simple_tokenize(query)
    scores = bm25.get_scores(tokens)
    ranked = sorted(zip(scores, corpus), key=lambda pair: pair[0], reverse=True)
    return [
        {"id": doc["id"], "title": doc["title"], "score": float(score), "doc": doc}
        for score, doc in ranked[:k]
    ]
    
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
        
if __name__ == "__main__":
    # """Dense retrieval on all queries"""
    # print(f"══ Dense retrieval on all 6 queries (top-1) ══\n")
    # print(f"  {'Expected':10s}  {'Query':<50s}  {'Retrieved':<20s}  Verdict")
    # print(f"  {'--------':10s}  {'-----':<50s}  {'---------':<20s}  -------")

    # dense_correct = 0
    # for tq in queries:
    #     hits = dense_search(tq["q"], k=1)
    #     got = hits[0]["id"]
    #     correct = got == tq["expected_id"]
    #     if correct: dense_correct += 1
    #     verdict = "✓" if correct else "✗ (expected " + tq["expected_id"] + ")"
    #     print(f"  {tq['expected_winner']:10s}  {tq['q'][:50]:<50s}  {got:<20s}  {verdict}")

    # print(f"\nDense-only: {dense_correct}/{len(queries)} correct at top-1")
    # Fit BM25
    print(f"\n══ Building BM25 index ══")
    tokenized_corpus = [simple_tokenize(d["text"] + " " + d["title"]) for d in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    # print(f"Indexed {len(corpus)} docs. Ready to query.")
    
    # print(f"══ BM25 retrieval on all 6 queries (top-1) ══\n")
    # print(f"  {'Expected':10s}  {'Query':<50s}  {'Retrieved':<20s}  Verdict")
    # print(f"  {'--------':10s}  {'-----':<50s}  {'---------':<20s}  -------")

    # bm25_correct = 0
    # for tq in queries:
    #     hits = bm25_search(tq["q"], k=1)
    #     got = hits[0]["id"]
    #     correct = got == tq["expected_id"]
    #     if correct: bm25_correct += 1
    #     verdict = "✓" if correct else "✗ (expected " + tq["expected_id"] + ")"
    #     print(f"  {tq['expected_winner']:10s}  {tq['q'][:50]:<50s}  {got:<20s}  {verdict}")

    # print(f"\nBM25-only: {bm25_correct}/{len(queries)} correct at top-1")
    
    # print(f"══ Dense vs BM25 side-by-side (top-1 each) ══\n")
    # print(f"  {'Query':<50s}  {'DENSE top-1':<20s}  {'BM25 top-1':<20s}  {'Correct':<10s}")
    # print(f"  {'-----':<50s}  {'-----------':<20s}  {'----------':<20s}  {'-------':<10s}")

    # dense_wins, bm25_wins, both_win, both_fail = 0, 0, 0, 0

    # for tq in queries:
    #     dense_top = dense_search(tq["q"], k=1)[0]
    #     bm25_top  = bm25_search(tq["q"], k=1)[0]
        
    #     dense_ok = dense_top["id"] == tq["expected_id"]
    #     bm25_ok  = bm25_top["id"]  == tq["expected_id"]
        
    #     if dense_ok and bm25_ok:     tag = "both ✓";     both_win += 1
    #     elif dense_ok:               tag = "dense only";  dense_wins += 1
    #     elif bm25_ok:                tag = "bm25 only";   bm25_wins += 1
    #     else:                        tag = "both ✗";     both_fail += 1
        
    #     d_mark = "✓" if dense_ok else " "
    #     b_mark = "✓" if bm25_ok else " "
    #     print(f"  {tq['q'][:50]:<50s}  {d_mark} {dense_top['id']:<18s}  {b_mark} {bm25_top['id']:<18s}  {tag}")

    # print()
    # print(f"Both right:         {both_win}/{len(queries)}")
    # print(f"Only dense right:   {dense_wins}/{len(queries)}")
    # print(f"Only BM25 right:    {bm25_wins}/{len(queries)}")
    # print(f"Both wrong:         {both_fail}/{len(queries)}")
    
    # Toy example to show RRF math
    print("══ RRF sanity check ══")
    list_bm25  = [{"id": "doc_A"}, {"id": "doc_B"}, {"id": "doc_C"}]
    list_dense = [{"id": "doc_C"}, {"id": "doc_A"}, {"id": "doc_D"}]

    print(f"  BM25 ranks:  {[h['id'] for h in list_bm25]}")
    print(f"  Dense ranks: {[h['id'] for h in list_dense]}")

    fused = rrf_fuse([list_bm25, list_dense], k=60, top_n=5)
    print(f"\n  RRF fused (k=60):")
    for h in fused:
        print(f"    {h['id']}  rrf_score = {h['rrf_score']:.5f}")

    print(f"\n  Interpretation:")
    print(f"  - doc_A ranks 1st and 2nd → score = 1/61 + 1/62 = {1/61 + 1/62:.5f}")
    print(f"  - doc_C ranks 3rd and 1st → score = 1/63 + 1/61 = {1/63 + 1/61:.5f}")
    print(f"  - doc_B appears in one list only → score = 1/62 = {1/62:.5f}")
    print(f"  - doc_D appears in one list only → score = 1/63 = {1/63:.5f}")