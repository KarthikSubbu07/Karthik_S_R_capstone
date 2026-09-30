## Setup
import os, re
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv, main
from corpus import documents

load_dotenv()
assert "OPENAI_API_KEY" in os.environ, "Please set the OPENAI_API_KEY environment variable."
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL"))

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL  = "gpt-4o-mini"

import mlflow

def chunk_text(text, size=200, overlap=40):
        if len(text) < size:
                return [text]
        chunks = []
        start = 0
        while start < len(text):
                chunk = text[start:start+size]
                chunks.append(chunk)
                start += size - overlap
        return chunks

def chunk_by_sentence(text):
    """Split on sentence boundaries. Simpler than a proper NLP splitter."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s]

def chunk_by_paragraph(text):
    """One chunk per paragraph."""
    return [p.strip() for p in text.split("\n\n") if p.strip()]

def embed_batch(texts):
        """One API call, list of 1536-dim vectors back."""
        resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
        return [item.embedding for item in resp.data]

def cosine(a, b):
    va, vb = np.array(a), np.array(b)
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))

def show_top_k(query, k=3):
    """Given a query, print the top-K chunks with their cosine scores."""
    q_vec = embed_batch([query])[0]
    scored = [(cosine(q_vec, c["vector"]), c) for c in all_chunks]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    print(f"\nQ: {query!r}")
    for i, (score, chunk) in enumerate(scored[:k], 1):
        print(f"  [{i}] {score:.3f}  {chunk['chunk_id']:<25s} {chunk['text'][:60]}...")
        
def retrieve(query, chunks, k=3):
    q_vec = embed_batch([query])[0]
    scored = [(cosine(q_vec, c["vector"]), c) for c in chunks]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [{**c, "score": s} for s, c in scored[:k]]

SYSTEM = (
    "You are a helpful assistant. Answer the user's question using ONLY the "
    "provided context. If the context does not contain the answer, say so "
    "plainly. Cite the source id in square brackets after any fact you use."
)

def build_prompt(question, retrieved, system=SYSTEM):
    context = "\n\n".join(
        f"[{hit['chunk_id']}]\n{hit['text']}"
        for hit in retrieved
    )
    user_msg = f"Context:\n{context}\n\n---\n\nQuestion: {question}"
    return system, user_msg

def ask_rag(question, chunks, k=3, system=SYSTEM):
    retrieved = retrieve(question, chunks, k=k)
    sys, user = build_prompt(question, retrieved, system=system)
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0.0,
        messages=[
            {"role": "system", "content": sys},
            {"role": "user",   "content": user},
        ],
    )
    return {
        "question":   question,
        "answer":     resp.choices[0].message.content,
        "sources":    [hit["chunk_id"] for hit in retrieved],
        "tokens_in":  resp.usage.prompt_tokens,
        "tokens_out": resp.usage.completion_tokens,
    }



if __name__ == "__main__":                    
        
        all_chunks = []
        for doc in documents:
                for chunk_idx, chunk in enumerate(chunk_text(doc["text"])):
                        all_chunks.append({
                        "chunk_id":  f"{doc['id']}#{chunk_idx}",
                        "source_id": doc["id"],
                        "text":      chunk,
                        })
                
        chunk_texts = [c["text"] for c in all_chunks]        
        vectors = embed_batch(chunk_texts)

        for chunk, vec in zip(all_chunks, vectors):
                chunk["vector"] = vec

        # print(f"Embedded {len(vectors)} chunks.")
        # print(f"Each embedding shape: {len(vectors[0])} dimensions")
        # print(f"\nFirst 8 dims of chunk 0 ({all_chunks[0]['chunk_id']}):")
        # print(f"  {vectors[0][:8]}")
        # print(f"\nFirst 8 dims of chunk 1 ({all_chunks[1]['chunk_id']}):")
        # print(f"  {vectors[1][:8]}")
        # print("\nTakeaway: embeddings are floats. You cannot read them by eye.")
        # print("But you CAN compute similarity between them — next cell.")
        
        # QUERY = "how is espresso made?"
        # query_vector = embed_batch([QUERY])[0]    
        # scored = [(cosine(query_vector, c["vector"]), c) for c in all_chunks]
        
        # print(f"Query: {QUERY!r}\n")
        # print(f"  {'cosine':>7s}  {'chunk_id':<30s}  preview")
        # print(f"  {'------':>7s}  {'--------':<30s}  {'-------':<50s}")
        # for score, chunk in scored[:10]:
        #         print(f"  {score:>7.3f}  {chunk['chunk_id']:<30s}  {chunk['text'][:50]}...")
        
        # show_top_k("how much caffeine is in tea?") 
        # show_top_k("what is a latte?")  
        QUERY = "what is a latte?"
        top3 = retrieve(QUERY, all_chunks, k=3)
        # for i, chunk in enumerate(top3, 1):
        #         print(f"  [{i}] {chunk['score']:.3f}  {chunk['chunk_id']:<25s} {chunk['text'][:60]}...")
        #         print(f"        {chunk['text']}\n")
                
        # system_msg, user_msg = build_prompt(QUERY, top3)

        # print("═══ SYSTEM ═══")
        # print(system_msg)
        # print("\n═══ USER ═══")
        # print(user_msg)
        
        # result = ask_rag(QUERY, all_chunks, k=3)
        # print(f"Q: {result['question']}\n")
        # print(f"A: {result['answer']}\n")
        # print(f"Sources retrieved: {result['sources']}")
        # print(f"Prompt tokens: {result['tokens_in']}  ·  Completion tokens: {result['tokens_out']}")
        
        # SYSTEM_STRICT = (
        # "You are a strict assistant. Answer ONLY from the context provided. "
        # "If the answer is not explicitly stated in the context, respond with "
        # "'The context does not contain this information.' Do not use any "
        # "knowledge from your training. Cite the source id after each fact."
        # )

        # SYSTEM_PERMISSIVE = (
        # "You are a helpful assistant. Use the context to answer, but you may "
        # "add helpful background from what you know if it clarifies the answer."
        # )

        # SYSTEM_NO_INSTRUCTION = (
        # "You are a helpful assistant."
        # )

        # test_query = "What is the ideal water temperature for oolong tea, and why?"

        # for label, sys_prompt in [
        #         ("STRICT     ", SYSTEM_STRICT),
        #         ("PERMISSIVE ", SYSTEM_PERMISSIVE),
        #         ("NO INSTRUCT", SYSTEM_NO_INSTRUCTION),
        # ]:
        #         r = ask_rag(test_query, all_chunks, k=3, system=sys_prompt)
        #         print(f"── {label} ──")
        #         print(f"   {r['answer']}")
        #         print(f"   sources: {r['sources']}\n")
        
        # r = ask_rag("how do you brew beer?", all_chunks, k=3)
        # print(f"Q: {r['question']}\n")
        # print(f"A: {r['answer']}\n")
        # print(f"Sources retrieved: {r['sources']}")
        
        # sys_msg, user_msg = build_prompt("how is espresso made?", [])
        # print("═══ USER MESSAGE WITH ZERO CONTEXT ═══")
        # print(user_msg)
        # print()

        # resp = client.chat.completions.create(
        # model=CHAT_MODEL,
        # temperature=0.0,
        # messages=[
        #         {"role": "system", "content": sys_msg},
        #         {"role": "user",   "content": user_msg},
        # ],
        # )
        # print("═══ ANSWER ═══")
        # print(resp.choices[0].message.content)
        
        # r = ask_rag("expresso how mak??", all_chunks, k=3)
        # print(f"Q: {r['question']}\n")
        # print(f"A: {r['answer']}\n")
        # print(f"Sources retrieved: {r['sources']}")
        
        r = ask_rag(
                "Compare the caffeine content of black tea and green tea, and the water "
                "temperatures used to brew them.",
        all_chunks, k=3,
        )
        print(f"Q: {r['question']}\n")
        print(f"A: {r['answer']}\n")
        print(f"Sources retrieved: {r['sources']}\n")
        print("Retrieved chunks (with content):\n")
        for hit in retrieve(r['question'], all_chunks, k=3):
                print(f"  [{hit['chunk_id']}] cosine={hit['score']:.3f}")
                print(f"    {hit['text'][:120]}...\n")
        
        # all_chunks = []
        # for doc in documents:
        #         for chunk_idx, chunk in enumerate(chunk_text(doc["text"])):
        #                 all_chunks.append({
        #                 "chunk_id":  f"{doc['id']}#{chunk_idx}",
        #                 "source_id": doc["id"],
        #                 "text":      chunk,
        #                 })
        # print(f"Total chunks from {len(documents)} documents: {len(all_chunks)}\n")
        # for c in all_chunks[:8]:  # show first 8 to avoid wall of text
        #         marker = "…" if len(c["text"]) == 200 else " "
        #         print(f"  {c['chunk_id']:30s} [{len(c['text']):3d} chars] {c['text'][:60]}{marker}")
        # print(f"  ... and {len(all_chunks) - 8} more chunks")
        # sample = documents[0]["text"]  # coffee_espresso
        # print(f"Sample document: {documents[0]['id']} ({len(sample)} chars)\n")
        # print(f"Text: {sample}\n")
        # print("═" * 80)
        
        
        # sw_chunks = chunk_text(sample)
        # print(f"\n1. SLIDING WINDOW (size=200, overlap=40) → {len(sw_chunks)} chunks")
        # for i, c in enumerate(sw_chunks):
        #         print(f"    [{i}] ({len(c):3d} chars) {c!r}")

        # sent_chunks = chunk_by_sentence(sample)
        # print(f"\n2. BY SENTENCE → {len(sent_chunks)} chunks")
        # for i, c in enumerate(sent_chunks):
        #         print(f"    [{i}] ({len(c):3d} chars) {c!r}")

        # para_chunks = chunk_by_paragraph(sample)
        # print(f"\n3. BY PARAGRAPH → {len(para_chunks)} chunks")
        # for i, c in enumerate(para_chunks):
        #         print(f"    [{i}] ({len(c):3d} chars) {c!r}")
        
        
        # for doc in documents:
        #         print(doc["id"])
        #         chunks = chunk_text(doc["text"])
        #         print(chunks)
        #         print("**************")