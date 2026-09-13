"""W4 STARTER — src/pipeline/pipeline.py

The W3 version of this file is your starting point. You'll modify three things:

  • ask_llm — switch to tool-calling so the LLM returns structured args
    matching your richer Answer shape (content, confidence, sources).
  • stream_answer — replace simulated streaming (asyncio.sleep) with real
    OpenAI streaming (stream=True + chunk.choices[0].delta.content).
  • cost wiring — read response.usage and compute real cost_usd via cost.py.

The W3 contract is sacred. The public shape of these functions does not
change — Question in, Answer out (or async generator of str for streaming).
"""
from __future__ import annotations

import asyncio
import logging
from typing import AsyncIterator

from openai import AsyncOpenAI

from .cost import compute_cost_usd
from .models import Answer, Question
from .settings import Settings

logger = logging.getLogger(__name__)


# ─── Tool schema for structured outputs (Step 1b) ───────────────────────────
# TODO Step 1b — define the answer_question tool schema below.
#
# The tool must declare three required parameters:
#   - content:    string
#   - confidence: number between 0 and 1
#   - sources:    array of strings (can be empty)
#
# OpenAI tool schema shape:
#   {"type": "function",
#    "function": {"name": "...",
#                 "description": "...",
#                 "parameters": {"type": "object",
#                                "properties": {...},
#                                "required": [...]}}}

ANSWER_TOOL = None  # TODO replace with the dict above


# ─── Fake LLM (kept from W2 for tests) ──────────────────────────────────────
async def fake_ask_llm(question: str) -> str:
    """Returns a canned answer with a small delay. Used by tests + offline runs."""
    await asyncio.sleep(0.05)
    return f"[FAKE] {question[:60]}"


# ─── Real LLM call via tool-calling (Step 1d, 1e + Step 2d) ─────────────────
async def ask_llm(q: Question, settings: Settings | None = None) -> Answer:
    """Call the LLM with tool-calling, returning a structured Answer.

    Retries on transient failures (kept from W2). Computes real cost from
    response.usage (Step 2d).
    """
    settings = settings or Settings()

    if settings.use_fake:
        # Test/offline path — unchanged from W2.
        content = await fake_ask_llm(q.question)
        return Answer(content=content, cost_usd=0.0, retries=0)

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    last_err: Exception | None = None

    for attempt in range(settings.max_retries + 1):
        try:
            # TODO Step 1d — call client.chat.completions.create with these args:
            #   model=settings.model,
            #   messages=[{"role": "user", "content": q.question}],
            #   tools=[ANSWER_TOOL],
            #   tool_choice={"type": "function",
            #                "function": {"name": "answer_question"}},
            #
            # The tool_choice forces the model to call OUR tool. Without it the
            # model might just reply in text.

            resp = None  # TODO replace with the await ... call above

            # TODO Step 1e — parse the tool call into Answer:
            # 1) Grab resp.choices[0].message.tool_calls[0].function.arguments
            #    (it's a JSON string).
            # 2) json.loads it.
            # 3) Build Answer(content=..., confidence=..., sources=..., retries=attempt,
            #                cost_usd=..., schema_version="v1").

            # TODO Step 2d — compute real cost:
            #   usage = resp.usage
            #   cost = compute_cost_usd(settings.model, usage.prompt_tokens,
            #                           usage.completion_tokens)
            # Pass cost into Answer above instead of the W3 placeholder.

            raise NotImplementedError("Steps 1d, 1e, 2d — fill these in")

        except Exception as exc:
            last_err = exc
            if attempt < settings.max_retries:
                await asyncio.sleep(settings.retry_delay_s * (2 ** attempt))
                continue
            raise

    raise RuntimeError(f"ask_llm exhausted retries: {last_err}")  # unreachable


# ─── Streaming endpoint (Step 2a, 2b) ───────────────────────────────────────
async def stream_answer(question: str, settings: Settings | None = None) -> AsyncIterator[str]:
    """Yield content tokens as they arrive from the LLM.

    W3 simulated this with asyncio.sleep. W4 replaces with real chunks.
    """
    settings = settings or Settings()

    if settings.use_fake:
        # Offline path — yield words slowly. Kept for tests.
        full = await fake_ask_llm(question)
        for word in full.split(" "):
            await asyncio.sleep(0.05)
            yield word + " "
        return

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    # TODO Step 2a — call client.chat.completions.create with stream=True:
    #   stream = await client.chat.completions.create(
    #       model=settings.model,
    #       messages=[{"role": "user", "content": question}],
    #       stream=True,
    #   )
    #
    # TODO Step 2b — iterate and yield:
    #   async for chunk in stream:
    #       delta = chunk.choices[0].delta
    #       if delta.content:
    #           yield delta.content

    raise NotImplementedError("Steps 2a, 2b — fill these in")
