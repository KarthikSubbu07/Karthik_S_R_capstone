# Week 2 — Hands-on Activity

**Title:** Stream answers as they finish — `as_completed` instead of `gather`.
**Time:** ~15–20 minutes
**Builds on:** the `pipeline.py` you built during the live session (the one with `fake_llm`).
**When to do this:** during the live session (after slide 28, "Run It — What We See", if there's time) — or as a 20-minute warm-up before starting the formal lab.

> The point of this activity isn't to write more code. It's to *see* what parallelism looks like when answers come back in the order they finish, not in the order they were asked. And to learn when each pattern (`gather` vs `as_completed`) is the right choice.

---

## Goal

Write a small variant of `run_batch` that uses `asyncio.as_completed` instead of `asyncio.gather`. Run it once cleanly and once with `fail_rate=0.4`. Watch the order in which answers print, and write two sentences on what you observed.

## Materials

- `src/pipeline/pipeline.py` from class (with `fake_llm` imported).
- A `docs/runs/week2-activity.md` file you'll create as you go.

---

## Steps

### 1. Add a new function next to `run_batch`

Open `pipeline.py` and add a `run_batch_stream` function. It does the same work as `run_batch` but prints each answer **the moment it arrives**:

```python
async def run_batch_stream(questions: list[Question], fail_rate: float = 0.0) -> list[Answer]:
    tasks = [ask_llm_with_retry(q, fail_rate=fail_rate) for q in questions]
    results: list[Answer] = []
    for coro in asyncio.as_completed(tasks):
        ans = await coro
        print(f"  ✓ {ans.text[:60]}...")            # arrives the instant it's ready
        results.append(ans)
    return results
```

### 2. Wire it into a temporary `__main__` block

Replace (or comment out) your usual `run_batch` call in `__main__` and try this for the activity:

```python
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
```

### 3. Run it cleanly first

```bash
python -m src.pipeline.pipeline
```

Watch the order of the `✓` lines as they print. Because `fake_ask_llm` sleeps for a *random* 0.3 – 1.5 s, the answers will print in **the order they finish**, not the order they were asked.

### 4. Now force some failures

```bash
python -m src.pipeline.pipeline 0.4
```

Same five questions, but with 40% chance of a transient failure per call. Watch what happens to the order: the questions that failed and retried will arrive **last**, because their 1 s / 2 s / 4 s backoffs push their wall-clock finish times out.

### 5. Reflect — two sentences in `docs/runs/week2-activity.md`

Open the file and answer:

- In one sentence: what did `as_completed` make visible that `gather` hides?
- In one sentence: when would you reach for `gather`, and when for `as_completed`?

---

## What you should notice

When you ran with `fail_rate=0.4`, the questions that needed a retry arrived **after** the others — sometimes seconds later — even though they were submitted at the same time. With `gather`, you couldn't have *seen* this: gather returns everything in one batch, in input order, when the slowest call finishes. With `as_completed`, the slowest call is visibly the slowest, and the fastest is visibly the fastest.

This is the engineering question: **when do you want the order, and when do you want the speed?**

- Use **`gather`** when you need all results before doing the next thing (90% of pipelines — including the W2 lab).
- Use **`as_completed`** when you want to start *processing* as results stream in, or to bail early on a first match (e.g., search ranking, "stop on first good answer", streaming-to-UI).

---

## Stretch (if you have ~5 extra minutes)

- **Add a concurrency cap.** Use `asyncio.Semaphore(3)` to limit yourself to 3 in-flight calls at a time. Watch the output — now answers print in batches of 3 even though they're "all in flight" conceptually. (This is the same pattern you'll see in real-world rate-limited APIs.)
- **Time it.** Add `time.time()` around the `asyncio.run(...)` call and print the elapsed seconds. Compare to a sync version of the same loop (which would take roughly the sum of all the sleeps).
- **Mix the patterns.** Try batches-of-3 *using* `as_completed` inside each batch. Notice how the patterns compose.

---

## Submit (optional but recommended)

Commit your `docs/runs/week2-activity.md` and the new function to your capstone repo:

```bash
git add src/pipeline/pipeline.py docs/runs/week2-activity.md
git commit -m "feat: W2 activity — run_batch_stream with as_completed"
```

Once you start the formal lab, **remove or comment out** `run_batch_stream` from `__main__` — the lab assumes `run_batch` / `run_in_batches`. (Keep the function definition; it's not in the way.)
