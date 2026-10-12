import os
import time
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from data import documents

load_dotenv()
assert os.getenv("OPENAI_API_KEY")
assert os.getenv("QDRANT_URL")
assert os.getenv("QDRANT_API_KEY")

client = OpenAI()

EMBED_SMALL = "text-embedding-3-small"    # 1536 dims, $0.02 per 1M tokens
EMBED_LARGE = "text-embedding-3-large"    # 3072 dims, $0.13 per 1M tokens

# print(f"Loaded {len(documents)} animals across 5 categories.\n")
# for d in documents:
#     print(f"  {d['id']:8s}  ({d['category']:7s})  {len(d['text']):3d} chars")

def embed_one(text: str, model: str = EMBED_SMALL) -> list[float]:
    resp = client.embeddings.create(model=model, input=[text])
    return resp.data[0].embedding

def embed_batch(texts, model=EMBED_SMALL):
    resp = client.embeddings.create(model=model, input=texts)
    return [item.embedding for item in resp.data]

def cosine(a, b):
    va, vb = np.array(a), np.array(b)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))

if __name__ == "__main__":
    # Embed all 10 animals in one API call
    texts = [d["text"] for d in documents]
    vectors = embed_batch(texts)

    # Attach the vector to each animal record
    for doc, vec in zip(documents, vectors):
        doc["vector"] = vec

    # print(f"Embedded {len(documents)} animals.\n")
    # for d in documents:
    #     print(f"  {d['id']:8s}  ({d['category']:7s})  dim={len(d['vector'])}")
        
        # Print the pairwise matrix as a formatted table
    ids = [d["id"] for d in documents]

    # Header row
    print(f"  {'':8s}", end="")
    for other_id in ids:
        print(f"{other_id[:6]:>7s}", end="")
    print()

    # Body
    for i, d in enumerate(documents):
        print(f"  {d['id']:8s}", end="")
        for j, other in enumerate(documents):
            if i == j:
                print(f"{'--':>7s}", end="")  # self-similarity is 1.0, skip
            else:
                score = cosine(d["vector"], other["vector"])
                print(f"{score:>7.3f}", end="")
        print(f"  ({d['category']})")

    print("\nRead across each row: which animals is this one most similar to?")
    print("Look for block structure — do same-category pairs score higher than cross-category?")