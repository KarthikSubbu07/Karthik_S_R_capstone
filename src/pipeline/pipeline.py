from __future__ import annotations

import argparse
import asyncio
import json
import time
import csv
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from typing import AsyncIterator

# Pipeline's internal Question type (W2 schema with text field)
class Question(BaseModel):
    """Internal pipeline question (not the public API type)."""
    text: str

# Pipeline's internal Answer type - extends fake_llm.Answer with W4 fields  
class Answer(BaseModel):
    """Internal pipeline answer (W2 base + W4 extensions)."""
    content: str
    cost_usd: float = 0.0001
    retries: int = 0
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    sources: list[str] = Field(default_factory=list)
    schema_version: str = "v1"

# Live-session stand-in. Same Pydantic shape as the real call.
try:
    from .logging_config import get_logger
    from .settings import Settings, RunSummary
    # from .models import Question
except ImportError:    
    from logging_config import get_logger
    from settings import Settings, RunSummary
    # from models import Question
    
log = get_logger("pipeline")
_settings_for_import = Settings()


if _settings_for_import.use_fake:
    try:
        from .fake_llm import fake_ask_llm, FakeLLMError
    except ImportError:
        from fake_llm import fake_ask_llm, FakeLLMError
else:
    from dotenv import load_dotenv
    from openai import AsyncOpenAI
    
    load_dotenv()
    _client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL")
    )    
        
        
## Tokle Schema for structured output
ANSWER_TOOL:dict = {
    "type": "function",
    "function": {
        "name": "answer_question",
        "description": "Returns a structured output for the answer with the following properties: content, confidence, and sources.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The answer in 2-4 sentences.",
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence score between 0 and 1.",
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Sources for the answer (can be empty).",
                },                 
            },
            "required": ["content", "confidence", "sources"]
        }
    }
}    
    
# Adding a load_questions function
def load_questions(csv_path: str | Path = None) -> list[Question]:
    if csv_path is None:
        csv_path = Path(__file__).resolve().parent.parent.parent / "data" / "questions.csv"
    questions = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            questions.append(Question(text=row['text']))
    return questions

# ---------- Step 2: one async call ----------
async def ask_llm(q: Question, fail_rate: float = 0.0) -> Answer:
    """One call. Live demo: fake. Lab: real AsyncOpenAI (same signature)."""
    log.info(f"asked: {q.text[:40]}")
    if _settings_for_import.use_fake:
        ans = await fake_ask_llm(q, fail_rate=fail_rate)
        print(ans)
        return Answer(
            content=args["content"],
            confidence=args["confidence"],
            sources=args.get("sources", []),
            cost_usd=0.0,
            retries=attempt,
            schema_version="v1",
        )
    else:
        # Implement the real AsyncOpenAI call here
        for attempt in range(_settings_for_import.max_retries + 1):
            try:
                response = await _client.chat.completions.create(
                    model=_settings_for_import.model,
                    messages=[
                        {"role": "user", 
                        "content": q.text}
                    ],
                    tools=[ANSWER_TOOL],
                    tool_choice={"type": "function",
                                "function": {"name": "answer_question"}},
                )
                tool_calls = response.choices[0].message.tool_calls
                if not tool_calls:
                    raise ValueError("No tool calls found in the response.")
                tool_args = tool_calls[0].function.arguments
                args = json.loads(tool_args)
                
                ## find the real cost
                # usage = response.usage
                # cost = co
                
                log.info(f"asked: {q.text[:40]}")

                return Answer(
                    content=args["content"],
                    confidence=args["confidence"],
                    sources=args.get("sources", []),
                    cost_usd=0.0,
                    retries=attempt,
                    schema_version="v1",
                )
            
            except Exception as exc:
                log.error(f"Attempt {attempt} failed for question: {q.text[:40]} ({exc})")
                if attempt == _settings_for_import.max_retries:
                    raise
                await asyncio.sleep(2**attempt)


# ---------- Step 3: retry with exponential backoff ----------
async def ask_llm_with_retry(
    q: Question, tries: int = 3, fail_rate: float = 0.0
) -> Answer:
    """Retry up to ``tries`` times. Wait 1 s, 2 s, 4 s between attempts."""
    for attempt in range(tries):
        try:
            ans = await ask_llm(q, fail_rate=fail_rate)
            ans.retries = attempt
            return ans

        except Exception as exc:
            if attempt == tries-1:
                raise
            log.warning(f"attempt {attempt+1} failed for question: {q.text[:40]} ({exc})")
            await asyncio.sleep(2**attempt)

    raise NotImplementedError("Step 3 — wrap ask_llm with retry + exponential backoff")

# ---------- Step 4: gather it all together ----------
async def run_batch(
    questions: list[Question], fail_rate: float = 0.0
) -> list[Answer]:
    """Fire all questions in parallel via ``asyncio.gather``."""

    tasks = [ask_llm_with_retry(q, fail_rate = fail_rate) for q in questions]
    return await asyncio.gather(*tasks)

# Week 2 assignment, collect responses as and when available using as_completed instead of gather.
async def run_batch_stream(
    questions: list[Question], fail_rate: float = 0.0
) -> list[Answer]:
    """Fire all questions in parallel via ``asyncio.gather``."""

    tasks = [ask_llm_with_retry(q, fail_rate = fail_rate) for q in questions]
    results: list[Answer] = []
    for coro in asyncio.as_completed(tasks):
        result = await coro
        print(f"{result.text[:60]}")
        results.append(result)

    return results



def summarise_run(
    answers: list[Answer],
    *, 
    started_at: float, 
    elapsed: float, 
    fail_rate: float, 
    use_fake: bool) -> RunSummary:
    """Summarise a run given the answers and metadata."""
    return RunSummary(
        started_at      = started_at,
        elapsed_seconds = elapsed,
        n_questions     = len(answers),
        n_succeeded     = len(answers),
        n_retries_total = sum(a.retries  for a in answers),
        total_cost_usd  = sum(a.cost_usd for a in answers),
        fail_rate       = fail_rate,
        use_fake        = use_fake,
    )


# Run in batches
async def run_in_batches(
    questions: list[Question],
    batch_size: int, 
    fail_rate: float = 0.0) -> list[Answer]:
    answers = []
    for i in range(0, len(questions), batch_size):
        chunk = questions[i:i + batch_size]
        log.info(f"batch {i // batch_size + 1}: {len(chunk)} questions")
        batch_answers = await asyncio.gather(*(ask_llm_with_retry(q, fail_rate=fail_rate) for q in chunk))
        answers.extend(batch_answers)
        await asyncio.sleep(0.1)  # yield control to the event loop
    return answers

# ─── Streaming endpoint (Step 2a, 2b) ───────────────────────────────────────
async def stream_answer(question: str, settings: Settings | None = None) -> AsyncIterator[str]:
    """Yield content tokens as they arrive from the LLM.

    W3 simulated this with asyncio.sleep. W4 replaces with real chunks.
    """
    # settings = settings or Settings()

    if _settings_for_import.use_fake:
        # Offline path — yield words slowly. Kept for tests.
        full = await fake_ask_llm(question)
        for word in full.split(" "):
            await asyncio.sleep(0.05)
            yield word + " "
        return
    else:
        # client = AsyncOpenAI(api_key=_settings_for_import.openai_api_key)
        stream = await _client.chat.completions.create(
            model=_settings_for_import.model,
            messages=[{"role": "user", "content": question}],
            stream=True,
        )
        
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

# ---------- main ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the LLM pipeline")
    parser.add_argument("--limit", type=int, default=None,
                        help="Process only the first N questions (useful for debugging)")
    args = parser.parse_args()
    
    settings = Settings()
    log.info(f"config: {settings.model_dump(mode='json')}")
    questions = load_questions(settings.questions_csv)
    
    if args.limit:
        questions = questions[:args.limit]
        log.info(f"limit applied: processing first {args.limit} of {len(questions)} questions")
    else:
        log.info(f"loaded {len(questions)} questions")
    started = time.time()    
    answers = asyncio.run(run_in_batches(questions, batch_size=settings.batch_size, fail_rate=settings.fail_rate))
    elapsed = time.time() - started

    summary = summarise_run(
        answers,
        started_at=started,
        elapsed=elapsed,
        fail_rate=settings.fail_rate,
        use_fake=settings.use_fake
    )
    log.info(f"summary: {summary.model_dump(mode='json')}")
    settings.results_json.write_text(
        json.dumps({
            "summary": summary.model_dump(mode='json'),
            "answers": [a.model_dump(mode='json') for a in answers]
        }, indent=2),
        encoding="utf-8",
        )
    
    print(f"wrote {len(answers)} answers to {settings.results_json} in {elapsed:.2f}s")
    from store import connect, write_run, write_answers
    with connect(settings.results_db) as con:
        run_id = write_run(con, summary)
        n = write_answers(con, run_id, answers)
        log.info(f"persisted run {run_id} with {n} answers to {settings.results_db}")
    
