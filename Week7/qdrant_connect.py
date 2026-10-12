
import os
from dotenv import load_dotenv
from qdrant_client.http.models import VectorParams, Distance
from qdrant_client import QdrantClient
from day1_embeddingSpace import embed_batch
from data import documents
load_dotenv()

assert os.getenv("QDRANT_URL")
assert os.getenv("QDRANT_API_KEY")

qdrant = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.environ["QDRANT_API_KEY"],
)

COLLECTION_NAME = "wk07_day1_animals"
# Create fresh
# qdrant.create_collection(
#     collection_name=COLLECTION_NAME,
#     vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
# )
# Sanity check — list existing collections
existing = qdrant.get_collections()
print(f"Connected to Qdrant at {os.environ['QDRANT_URL'][:40]}...")
print(f"Existing collections: {[c.name for c in existing.collections]}")

from qdrant_client.models import PointStruct
texts = [d["text"] for d in documents]
vectors = embed_batch(texts)

# Attach the vector to each animal record
for doc, vec in zip(documents, vectors):
    doc["vector"] = vec

points = [
    PointStruct(
        id=idx,
        vector=doc["vector"],
        payload={
            "animal_id": doc["id"],
            "category":  doc["category"],
            "text":      doc["text"],
        },
    )
    for idx, doc in enumerate(documents)
]

qdrant.upsert(collection_name=COLLECTION_NAME, points=points)

# Verify
info = qdrant.get_collection(COLLECTION_NAME)
print(f"Upserted {len(points)} points.")
print(f"Collection now has {info.points_count} points.")