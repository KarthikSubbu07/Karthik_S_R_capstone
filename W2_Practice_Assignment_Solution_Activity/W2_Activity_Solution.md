# W2 Activity Solution — `as_completed` vs `gather`

> *Instructor reference for the W2 streaming activity. The point of
> this exercise is to make parallelism visible — `as_completed`
> reveals what `gather` hides.*

**Activity time:** 15-20 min
**Stretch time:** +5 min
**Files involved:** `src/pipeline/pipeline.py` (existing) + `docs/runs/week2-activity.md` (new)

---

## What this activity is testing

Two outcomes:

1. **Pattern recognition** — when do you want `gather` (all-or-nothing
   batch) vs `as_completed` (stream as results arrive)?
2. **Visible parallelism** — `as_completed` makes it obvious that
   slower calls finish later; `gather` hides this entirely behind a
   single batch return.

This is foundational for W3 (FastAPI streaming), W22 (observability),
and any time learners reason about concurrent LLM calls.

---

## Reference solution walkthrough

### The new function

```python
async def run_batch_stream(questions: list[Question],
                            fail_rate: float = 0.0) -> list[Answer]:
    tasks = [ask_llm_with_retry(q, fail_rate=fail_rate) for q in questions]
    results: list[Answer] = []
    for coro in asyncio.as_completed(tasks):
        ans = await coro
        print(f"  ✓ {ans.text[:60]}...")
        results.append(ans)
    return results
```

Three things matter here:

1. **`asyncio.as_completed(tasks)` returns an iterator** that yields
   coroutines in *completion order*, not submission order
2. **Each `await coro` blocks only until the next-fastest call
   finishes** — so the print statement runs the moment a result is
   ready
3. **`results` is in completion order**, not in the order of the
   input `questions` list

### Sample output — clean run (`fail_rate=0.0`)

```
run_batch_stream — fail_rate=0.0
  ✓ Async means non-blocking, await pauses execution until ready...
  ✓ A chatbot answers within a conversation; an agent takes action...
  ✓ Vector databases store embeddings, do similarity search, scale...
  ✓ LLMs hallucinate because they're generative — they predict tokens...
  ✓ RAG is Retrieval-Augmented Generation — fetch context, then answer...

returned 5 answers
```

The order is **random across runs** because `fake_ask_llm` sleeps for a
random 0.3-1.5s. Each learner's output will differ slightly. That's the
point.

### Sample output — with failures (`fail_rate=0.4`)

```
run_batch_stream — fail_rate=0.4
  ✓ Async means non-blocking, await pauses execution until ready...
  ✓ A chatbot answers within a conversation; an agent takes action...
  ✓ Vector databases store embeddings, do similarity search, scale...
  ✓ LLMs hallucinate because they're generative — they predict tokens...
  ✓ RAG is Retrieval-Augmented Generation — fetch context, then answer...

returned 5 answers
```

Note: the wall-clock time will be longer, and the questions that
retried will arrive *last*. Their print lines will appear several
seconds after the others — the retry backoffs (1s, 2s, 4s) compound
the wait.

### The reflection — what learners should write

A good answer to "what did `as_completed` make visible that `gather`
hides?":

> `gather` returns all results in input order at the moment the
> slowest call finishes. `as_completed` shows me the actual finish
> order, so I can see which calls are slow and which are fast.

A good answer to "when would you reach for `gather` vs
`as_completed`?":

> `gather` when I need all results before continuing (most pipelines,
> including the W2 lab). `as_completed` when I want to start
> processing as results stream in — streaming-to-UI, early stopping
> on first match, or surfacing the fastest answer.

---

## What to look for in submissions

**Strong signals:**
- The function uses `asyncio.as_completed(tasks)` correctly (iterates,
  awaits each coro)
- The output ordering observation explicitly notes "completion order,
  not input order"
- The reflection identifies a real use case for each pattern (not
  hand-waving)

**Weak signals:**
- Confuses `as_completed` with `gather(*tasks, return_exceptions=True)`
- Reflection that says *"as_completed is better"* without identifying
  when `gather` is right
- Output doesn't show the timing effect (probably ran with a fixed
  `sleep` instead of the random `fake_ask_llm` sleep)

**Common mistakes:**
- Forgets `await coro` — gets a coroutine object printed, not the
  result
- Iterates over `tasks` directly instead of `as_completed(tasks)`
- Calls `asyncio.gather` after `as_completed` — defeats the purpose

---

## Stretch outcomes

For learners who attempted the stretch:

- **Concurrency cap with Semaphore.** Wrap each task in
  `async with sem:` and watch results print in batches of 3 (or
  whatever the cap is). The cap is invisible without `as_completed`.
- **Timing.** Sync version takes ~5s for 5 questions (sum of sleeps).
  Async version takes ~max sleep (~1.5s). Roughly 3-4x speedup.
- **Composed pattern.** Batches-of-3 with `as_completed` inside each
  batch is the real-world pattern for rate-limited APIs.

---

## Office hours hot questions

- *"My answers print in different orders each run. Is that a bug?"* —
  No, that's the lesson. `fake_ask_llm` sleeps for a random duration,
  so finish order varies.
- *"With `fail_rate=0.4`, my run takes 10+ seconds. Why?"* — Retries
  with exponential backoff (1s, 2s, 4s) compound the wait. Real APIs
  use similar backoffs; this is faithful.
- *"Should I use `as_completed` in the lab?"* — No, the W2 lab needs
  ordered results. Use `gather` (or `run_in_batches`).

---

## Files in this solution package

- `pipeline_solution.py` — complete `pipeline.py` with `run_batch`,
  `run_batch_stream`, `fake_ask_llm`, and the `__main__` block
- `sample_outputs.md` — clean run + fail_rate=0.4 run side-by-side
- `sample_week2-activity.md` — what a strong learner submission looks like

---

*End of W2 solution.*
