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

import asyncio
import json
import logging
import time
import sys
import csv
from pathlib import Path

# Live-session stand-in. Same Pydantic shape as the real call.
try:
    from .fake_llm import Question, Answer, fake_ask_llm, FakeLLMError
    from .logging_config import get_logger
    from .settings import Settings
except ImportError:
    from fake_llm import Question, Answer, fake_ask_llm, FakeLLMError
    from logging_config import get_logger
    from settings import Settings
log = get_logger("pipeline")


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
    return await fake_ask_llm(q, fail_rate=fail_rate)
    
    # TODO (Step 5): once logging is configured, also log here, e.g.
    #                log.info(f"asked: {q.text[:40]}")
    raise NotImplementedError("Step 2 — call fake_ask_llm and return the Answer")


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

    
    # TODO (Step 3):
    #   for attempt in range(tries):
    #       try:
    #           ans = await ask_llm(q, fail_rate=fail_rate)
    #           ans.retries = attempt
    #           return ans
    #       except Exception:
    #           if attempt == tries - 1:
    #               raise
    #           await asyncio.sleep(2 ** attempt)
    


# ---------- Step 4: gather it all together ----------
async def run_batch(
    questions: list[Question], fail_rate: float = 0.0
) -> list[Answer]:
    """Fire all questions in parallel via ``asyncio.gather``."""

    tasks = [ask_llm_with_retry(q, fail_rate = fail_rate) for q in questions]
    return await asyncio.gather(*tasks)


# # ---------- Step 5: structured (JSON) logging ----------
# # TODO (Step 5):
# class JsonFormatter(logging.Formatter):
#     def format(self, record):
#         import json
#         log_record = {
#             "ts": self.formatTime(record, self.datefmt),
#             "level": record.levelname,
#             "msg": record.getMessage(),
#         }
#         return json.dumps(log_record)
    
# log = logging.getLogger("pipeline")
# log.setLevel(logging.INFO)
# _handler = logging.StreamHandler()
# _handler.setFormatter(JsonFormatter())
# log.addHandler(_handler)

# ---------- main ----------
if __name__ == "__main__":
    settings = Settings()
    log.info(f"config: {settings.model_dump(mode='json')}")
    
    
    # fail_rate = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    
    sample = [
        Question(text="What is RAG in one sentence?"),
        Question(text="Name three uses of vector databases."),
        Question(text="Why might an LLM hallucinate?"),
    ]
    started = time.time()
    answers = asyncio.run(run_batch(sample, fail_rate=settings.fail_rate))
    elapsed = time.time() - started
    print(f"\n{len(answers)} answers in {elapsed:.2f}s\n")
    for a in answers:
        print(f"- {a.text[:80]}")
