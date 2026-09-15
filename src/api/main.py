"""api/main.py — STARTER for Week 3 Lab Step 1.

You will complete this file across sub-steps 1b → 1f. Each TODO matches a
sub-step in the lab guide.

The completed reference is at <cohort-repo>/week3/reference/api_main_reference.py.

Architecture note: this file holds the *public* W3 API contract — Question
with field `question`, Answer with fields `content/cost_usd/retries`. These
are locked in ADR 0002. Internally we delegate to the W2 pipeline's
`ask_llm`, whose Question has field `text` and whose Answer has field `text`.
The translation happens inside each endpoint.
"""
import sys
from pathlib import Path

# Add repo root to path so we can import src
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import logging
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# W2 pipeline — the underlying engine
from src.pipeline.pipeline import ask_llm as _pipeline_ask_llm, stream_answer
from src.pipeline.pipeline import Question as _PipelineQuestion
from src.pipeline.pipeline import _settings_for_import
from src.pipeline.store import connect, save_answer

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Public W3 API models — locked in ADR 0002
# ─────────────────────────────────────────────────────────────────────────────
class Question(BaseModel):
    """Public request shape. Field name `question`, not `text`."""
    question: str


class Answer(BaseModel):
    """Public response shape. Field name `content`, not `text`."""
    content: str
    cost_usd: float
    retries: int
    confidence: float = 1.0
    sources: list[str] = []
    schema_version: str = "v1"


# ─────────────────────────────────────────────────────────────────────────────
# 1b — Replace the placeholder below with a real FastAPI app instance.
# ─────────────────────────────────────────────────────────────────────────────
app = None  # TODO 1b — replace with FastAPI(title="...", description="...", version="...")
app = FastAPI(
    title="AICapstoneAPI",
    description="API for the Agentic AI Capstone project",
    version="1.0.0",
)

## Week 2 assignment — request counting middleware
request_counts: dict[str, int] = {}
@app.middleware("http")
async def count_requests(request, call_next):
    path = request.url.path
    if path == "/metrics":
        return await call_next(request)
    request_counts[path] = request_counts.get(path, 0) + 1
    response = await call_next(request)
    return response

# TODO 1c — add /ask_batched here
@app.post("/ask_batched", response_model=Answer)
async def ask_batched(q: Question) -> Answer:
    pipeline_q = _PipelineQuestion(question=q.question)
    pipeline_ans = await _pipeline_ask_llm(pipeline_q)
    db_path = Path(__file__).resolve().parents[2] / "data" / "answers.db"
    with connect(db_path) as conn:
        save_answer(
            conn,
            question=q.question,
            content=pipeline_ans.content,
            retries=pipeline_ans.retries,
            cost_usd=pipeline_ans.cost_usd,
            model=_settings_for_import.model,
            confidence=pipeline_ans.confidence,
            sources=pipeline_ans.sources,
            schema_version=pipeline_ans.schema_version,
        )
    return Answer(
        content=pipeline_ans.content,
        confidence=pipeline_ans.confidence,
        sources=pipeline_ans.sources,
        cost_usd=pipeline_ans.cost_usd,
        retries=pipeline_ans.retries,
        schema_version=pipeline_ans.schema_version
    )
           
# ─────────────────────────────────────────────────────────────────────────────
# 1d — Add /health.
# ─────────────────────────────────────────────────────────────────────────────

# TODO 1d — add @app.get("/health") returning {"status": "ok"}
@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

@app.post("/ask")
async def ask(q: Question):
    """Streaming /ask endpoint."""
    """Real Streaming Response in text/plain."""
    async def _gen():
        async for chunk in stream_answer(q.question):
            yield chunk
    return StreamingResponse(_gen(), media_type="text/plain")
       
@app.get("/metrics")
async def metrics():
    return {"endpoints:": request_counts, "total": sum(request_counts.values())}
