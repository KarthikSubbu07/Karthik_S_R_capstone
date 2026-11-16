# """MP2 · Mini-RAG — Starter Template
# ====================================

# You'll build a complete RAG pipeline over the Sherlock Holmes corpus in this
# file. Fill in every TODO. The reference solution is ~250 lines, but yours can
# be shorter or longer — what matters is that it works end-to-end.

# Pipeline you're building:
#     corpus/*.txt  →  chunks  →  embeddings  →  Qdrant
#                                                   ↓
#                               question  →  retrieve  →  answer + citations

# Run sequence (once you've filled in the TODOs):
#     pip install -r requirements.txt
#     source .env                 # exports your OpenAI + Qdrant credentials
#     python mp2_rag.py ingest    # builds the collection (run once)
#     python mp2_rag.py ask       # interactive Q&A loop
#     python mp2_rag.py validate  # runs against data/predefined_questions.jsonl

# Tip: get the CORE pipeline working FIRST (Steps 1-7 below), THEN come back to
# polish and add your 3 questions. Don't try to perfect each step before moving
# on — you'll learn more from a rough end-to-end loop than a polished half.
# """
from __future__ import annotations

import json
import os
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from flask.cli import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
import truststore

# ─── Configuration ──────────────────────────────────────────────────────

CORPUS_DIR        = Path(__file__).parent / "corpus"
DATA_DIR          = Path(__file__).parent / "data"
COLLECTION_NAME   = "mp2_sherlock"
EMBEDDING_MODEL   = "text-embedding-3-small"
EMBEDDING_DIM     = 1536
CHAT_MODEL        = "gpt-4o-mini"
TARGET_CHUNK_SIZE = 500   # characters
CHUNK_OVERLAP     = 80    # characters

load_dotenv()

truststore.inject_into_ssl()
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
qdrant = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.environ.get("QDRANT_API_KEY"),
)


# ─── Step 1: Load the corpus ────────────────────────────────────────────
def load_corpus(corpus_dir: Path) -> list[dict[str, Any]]:
    """Read every .txt file in the corpus directory.

    Returns a list of dicts, each with: source (filename), title (first line),
    and text (full content).
    """
    ### Get list of all .txt files in the corpus directory
    txt_files = list(corpus_dir.glob("*.txt"))
    corpus_documents = []

    ## Iterate over each .txt file and extract metadata [source and title] and full text
    for file in txt_files:
        with open(file, "r", encoding="utf-8") as f:
            source = file
            full_text = f.read()
            title = full_text.split("\n", 1)[0]  # first line as title
            corpus_documents.append({"source": source, "title": title, "text": full_text})

    return corpus_documents
        
# ─── Step 2: Chunk each document ────────────────────────────────────────
def is_heading(block):
    return (
        "\n" not in block                              # single line
        and len(block.split()) <= 8                    # short
        and not block.endswith((".", ",", ";", ":", "!", "?", '"'))
    )

def chunk_by_paragraph(path):
    text = Path(path).read_text(encoding="utf-8")
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]

    chunks, section = [], None
    for block in blocks:
        if is_heading(block):
            section = block
        else:
            # normalise stray tabs/newlines inside a paragraph
            paragraph = re.sub(r"\s+", " ", block).strip()
            chunks.append({"section": section, "chunk": paragraph})                        

    return chunks


def chunk_document(doc: dict[str, Any]) -> list[dict[str, Any]]:
    """Split a document into smaller chunks.
    Each chunk should be a dict with: source, title, section, text."""
    
    # Smart approach: use chunk_by_paragraph and then pack paragraphs into chunks
    chunks = []
    for c in chunk_by_paragraph(doc["source"]):
        section = c["section"]
        text = c["chunk"]
        if chunks and len(chunks[-1]["text"]) + len(text) + CHUNK_OVERLAP <= TARGET_CHUNK_SIZE:
            # append to the last chunk
            chunks[-1]["text"] += " " + text
        else:
            chunks.append({
                "source": doc["source"],
                "title": doc["title"],
                "section": section,
                "text": text
            })

    return chunks


# ─── Step 3: Embed text ─────────────────────────────────────────────────

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch-embed a list of texts using OpenAI's embedding model.
    Returns a list of 1536-dim float vectors (same order as inputs).
    """
    
    resp = openai.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in resp.data]


# ─── Step 4: Set up the Qdrant collection ───────────────────────────────

def setup_collection() -> None:
    """Create (or recreate) the Qdrant collection."""
    qdrant = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.environ["QDRANT_API_KEY"]
    )
    
    # Create Collection
    if qdrant.collection_exists(collection_name=COLLECTION_NAME):
        qdrant.delete_collection(collection_name=COLLECTION_NAME)
        
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
    )
    
    # Sanity check — list existing collections
    existing = qdrant.get_collections()
    print(f"Connected to Qdrant at {os.environ['QDRANT_URL'][:40]}...")


# ─── Step 5: Ingest chunks into Qdrant ──────────────────────────────────

def ingest_chunks(chunks: list[dict[str, Any]]) -> None:
    """Embed every chunk and upsert into Qdrant.

    TODO:
      - Call embed_texts on the chunk texts
      - Build PointStruct objects (id=uuid, vector, payload=chunk dict)
      - qdrant.upsert
    """
    
    vectors = embed_texts([chunk["text"] for chunk in chunks])
    print(len(vectors))
    
    for chunk, vec in zip(chunks, vectors):
        chunk["vector"] = vec
        chunk["id"] = str(uuid.uuid4())
        
    points = [
        PointStruct(
            id=chunk["id"],
            vector=chunk["vector"],
            payload=chunk,
        )
        for chunk in chunks
    ]
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Upserted {len(points)} points into Qdrant collection '{COLLECTION_NAME}'.")
        

# ─── Step 6: Retrieve ───────────────────────────────────────────────────

def retrieve(query: str, k: int = 3) -> list[dict[str, Any]]:
    """Retrieve top-k chunks for a query.

    TODO:
      - Embed the query
      - qdrant.search with the query vector, limit=k
      - Return list of chunk dicts (include score for citations)
    """
    
    q_vec = embed_texts([query])[0]
    hits = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=q_vec,
        limit=k,
    ).points
    
    
    return [{"score": hit.score, **hit.payload} for hit in hits]


# ─── Step 7: Generate the answer ────────────────────────────────────────

SYSTEM_PROMPT = """You are a helpful assistant answering questions about a small
collection of Sherlock Holmes stories. You will be given the user's question and
several relevant excerpts. Use ONLY the provided excerpts to answer. If the
excerpts don't contain the answer, say so plainly. Cite the source (story title
+ section) in your answer."""


def answer(question: str, k: int = 3) -> dict[str, Any]:
    """End-to-end: retrieve, format context, call LLM, return result.

    TODO:
      - Call retrieve(question, k=k)
      - Format the retrieved chunks into a context string
        (include "[Source: <title> — <section>]" before each)
      - Call openai.chat.completions.create with SYSTEM_PROMPT and the user message
      - Return dict with: question, answer, citations, latency_ms
    """
    
    retrieved_chunks = retrieve(question, k=k)    
    user_message = f"Question: {question}\n\n"
    # for i, chunk in enumerate(retrieved_chunks, start=1):
    for chunk in retrieved_chunks:
        user_message += f"[Source: {chunk['title']} — {chunk['section']}]\n{chunk['text']}\n\n"
        
    openai_response = openai.chat.completions.create(
        model=CHAT_MODEL,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
    )

    return {
        "question": question,
        "answer": openai_response.choices[0].message.content,
        "citations": [{"source": chunk["source"].split("/")[-1], "section": chunk["section"]} for chunk in retrieved_chunks],
        "score": [{"score": chunk["score"]} for chunk in retrieved_chunks],
        "latency_ms": openai_response.response_ms if hasattr(openai_response, "response_ms") else None,
    }



# ─── Validation harness (provided — do not modify) ──────────────────────
def validate_against(jsonl_path: Path) -> None:
    questions = [json.loads(line) for line in jsonl_path.read_text().splitlines() if line.strip()]
    print(f"\n  Validating {len(questions)} questions from {jsonl_path.name}…\n")

    hits = 0
    for q in questions:
        result = answer(q["question"], k=6)
        cited_sources = {cit["source"] for cit in result["citations"]}
        source_hit = q["expected_source"] in cited_sources

        ans_lower = result["answer"].lower()
        facts_hit = sum(1 for fact in q.get("expected_facts", []) if fact.lower() in ans_lower)
        facts_total = len(q.get("expected_facts", []))

        verdict = "✓" if source_hit else "✗"
        print(f"  {verdict} {q['id']}")
        print(f"      Q: {q['question']}")
        print(f"      Cited: {', '.join(cited_sources)}")
        print(f"      Expected: {q['expected_source']}")
        print(f"      Facts matched: {facts_hit}/{facts_total}")
        print(f"      Latency: {result.get('latency_ms', '?')}ms")
        print()
        if source_hit:
            hits += 1

    print(f"  Source-match: {hits}/{len(questions)}")


# ─── CLI (provided — do not modify) ─────────────────────────────────────

def cmd_ingest() -> None:
    print("→ Loading corpus…")
    docs = load_corpus(CORPUS_DIR)
    print(f"  {len(docs)} documents loaded")

    print("→ Chunking…")
    all_chunks: list[dict[str, Any]] = []
    for doc in docs:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
        print(f"  {doc['title']}: {len(chunks)} chunks")

    print(f"→ Total chunks: {len(all_chunks)}")
    print("→ Setting up Qdrant collection…")
    setup_collection()

    print("→ Ingesting…")
    ingest_chunks(all_chunks)
    print("\n✓ Done. Try: python mp2_rag.py ask")


def cmd_ask() -> None:
    print("Mini-RAG over the Sherlock Holmes corpus.")
    print("Type your question. Empty line or Ctrl-C to exit.\n")
    while True:
        try:
            q = input("? ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not q:
            return
        result = answer(q, k=3)
        print(f"\n{result['answer']}\n")
        print("  Sources:")
        for c in result["citations"]:
            print(f"    - {c['source']} — {c['section']}")
        print(f"  Latency: {result.get('latency_ms', '?')}ms\n")


def cmd_validate() -> None:
    validate_against(DATA_DIR / "predefined_questions.jsonl")
    learner_path = DATA_DIR / "learner_questions.jsonl"
    if learner_path.exists():
        first = json.loads(learner_path.read_text().splitlines()[0])
        if not first["question"].startswith("Replace this"):
            validate_against(learner_path)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd == "ingest":   
        cmd_ingest()
    elif cmd == "ask":    
        cmd_ask()
    elif cmd == "validate": 
        cmd_validate()
    else:
        print(f"Unknown command: {cmd}\n")
        print(__doc__)
        sys.exit(1)
        
    ### Get list of all .txt files in the corpus directory
    ### Iterate over each .txt file and extract metadata [ source and title] and full text


if __name__ == "__main__":
    main()
    
