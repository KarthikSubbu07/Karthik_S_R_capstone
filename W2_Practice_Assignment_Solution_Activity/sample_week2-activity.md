# Week 2 Activity — `as_completed` vs `gather`

**Function added:** `run_batch_stream` in `src/pipeline/pipeline.py`

## Clean run output (`fail_rate=0.0`)

```
run_batch_stream — fail_rate=0.0
  ✓ Stub answer for: What is the difference between a chat...
  ✓ Stub answer for: Why might an LLM hallucinate?...
  ✓ Stub answer for: Explain async and await in plain langu...
  ✓ Stub answer for: What is RAG in one sentence?...
  ✓ Stub answer for: Name three uses of vector databases....

returned 5 answers
```

Notice the order is **not** the input order — answers print as they
finish. Each run produces a different order because the sleeps are
random.

## With failures (`fail_rate=0.4`) output

```
run_batch_stream — fail_rate=0.4
  ✓ Stub answer for: Name three uses of vector databases....
  ✓ Stub answer for: Explain async and await in plain langu...
  ✓ Stub answer for: What is the difference between a chat...
  ✓ Stub answer for: What is RAG in one sentence?...
  ✓ Stub answer for: Why might an LLM hallucinate?...

returned 5 answers
```

This run took ~6 seconds — about 5s longer than the clean run. The
last two answers retried at least once (1s + 2s backoff each).

## What I observed

- `as_completed` made the **order of completion visible**. With
  `fail_rate=0.4`, the two answers that retried arrived last —
  several seconds after the others — proving the retry backoff was
  real, not just folklore. `gather` would have hidden this completely
  by returning everything in one batch at the end.
- I'd use **`gather`** when I need all results before doing the next
  thing (most pipelines, including the W2 lab itself — the
  aggregation step needs all 5 answers). I'd use **`as_completed`**
  when I want to stream results to a UI as they arrive, or to bail
  early when the first acceptable answer comes back (e.g., search
  ranking where any decent hit is enough).
