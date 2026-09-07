"""pipeline.py — Week 2 hands-on starter.

We'll fill in the TODOs together during the live session. The pieces:

    Step 2 — async def ask_llm                 (one call)
    Step 3 — ask_llm_with_retry                (exponential backoff)
    Step 4 — run_batch with asyncio.gather     (parallel fan-out)
    Step 5 — JSON-formatted structured logging

For the live demo we call ``fake_ask_llm`` from ``fake_llm.py`` —
no API quota, no network flakiness, and a ``fail_rate`` knob so retries
fire on demand. In the lab you'll swap to the real ``AsyncOpenAI`` client
(same ``Question``/``Answer`` shape — only one import changes).

Run it (after the TODOs are filled):
    python pipeline.py           # fail_rate = 0.0  (clean parallel run)
    python pipeline.py 0.4       # fail_rate = 0.4  (forces retries)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import time
import csv
import os
from pathlib import Path

# Live-session stand-in. Same Pydantic shape as the real call.
try:
    from .logging_config import get_logger
    from .settings import Settings, RunSummary
except ImportError:    
    from logging_config import get_logger
    from settings import Settings, RunSummary
    
log = get_logger("pipeline")

_settings_for_import = Settings()


if _settings_for_import.use_fake:
    try:
        from .fake_llm import Question, Answer, fake_ask_llm, FakeLLMError
    except ImportError:
        from fake_llm import Question, Answer, fake_ask_llm, FakeLLMError
else:
    from dotenv import load_dotenv
    from openai import AsyncOpenAI
    from pydantic import BaseModel
    
    load_dotenv()
    _client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL")
    )
    
    class Question(BaseModel):
        text: str

    class Answer(BaseModel):
        question: str
        text: str
        cost_usd: float
        retries: int = 0
    
# Adding a load_questions function
def load_questions(csv_path: str | Path = "data/questions.csv") -> list[Question]:
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
        answer =  await fake_ask_llm(q, fail_rate=fail_rate)
    else:
        # Implement the real AsyncOpenAI call here
        response = await _client.chat.completions.create(
            model=_settings_for_import.model,
            messages=[
                {"role": "user", 
                 "content": q.text}
            ]
        )
        answer = Answer(
            question=q.text,
            text=response.choices[0].message.content,
            cost_usd=0.00,  # Replace with actual cost calculation if available
        )
    log.info(f"asked: {q.text[:40]}")
    # TODO (Step 5): once logging is configured, also log here, e.g.
    #                log.info(f"asked: {q.text[:40]}")
    return answer


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

# # ---------- main ----------
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Run the LLM pipeline")
#     parser.add_argument("--limit", type=int, default=None,
#                         help="Process only the first N questions (useful for debugging)")
#     args = parser.parse_args()
    
#     settings = Settings()
#     log.info(f"config: {settings.model_dump(mode='json')}")
#     questions = load_questions(settings.questions_csv)
    
#     if args.limit:
#         questions = questions[:args.limit]
#         log.info(f"limit applied: processing first {args.limit} of {len(questions)} questions")
#     else:
#         log.info(f"loaded {len(questions)} questions")
#     started = time.time()    
#     answers = asyncio.run(run_in_batches(questions, batch_size=settings.batch_size, fail_rate=settings.fail_rate))
#     elapsed = time.time() - started

#     summary = summarise_run(
#         answers,
#         started_at=started,
#         elapsed=elapsed,
#         fail_rate=settings.fail_rate,
#         use_fake=settings.use_fake
#     )
#     log.info(f"summary: {summary.model_dump(mode='json')}")
#     settings.results_json.write_text(
#         json.dumps({
#             "summary": summary.model_dump(mode='json'),
#             "answers": [a.model_dump(mode='json') for a in answers]
#         }, indent=2),
#         encoding="utf-8",
#         )
    
#     print(f"wrote {len(answers)} answers to {settings.results_json} in {elapsed:.2f}s")
#     from store import connect, write_run, write_answers
#     with connect(settings.results_db) as con:
#         run_id = write_run(con, summary)
#         n = write_answers(con, run_id, answers)
#         log.info(f"persisted run {run_id} with {n} answers to {settings.results_db}")
    

## Week 2 assignment run     
if __name__ == "__main__":
    import sys
    fail_rate = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    sample = [Question(text=t) for t in [
        "What is RAG in one sentence?",
        "Name three uses of vector databases.",
        "Why might an LLM hallucinate?",
        "Explain async and await in plain language.",
        "What is the difference between a chatbot and an agent?",
    ]]
    print(f"\nrun_batch_stream — fail_rate={fail_rate}")
    answers = asyncio.run(run_batch_stream(sample, fail_rate=fail_rate))
    print(f"\nreturned {len(answers)} answers")    
