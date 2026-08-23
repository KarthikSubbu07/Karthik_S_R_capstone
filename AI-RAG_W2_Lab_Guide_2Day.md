# Week 2 Lab — Async Batch Pipeline

**Programme:** Agentic AI & RAG Engineering
**Estimated time:** ~3 hours total · **Environment:** Vocareum (Python 3.11, OpenAI key pre-configured)
**Pacing:** Typically split across the two W2 days — Step 1 after Day 1, Steps 2–4 after Day 2. See *How to pace this* below.
**Companion files in the cohort repo** (all pre-uploaded to your lab environment) — see *Reference files* section below for full inventory.

---

## What we're building this week

This lab builds an async batch pipeline as a real engineering artefact — a typed, CSV-driven, retry-aware, JSON-logging, SQLite-persisted Python package that talks to the real OpenAI API. We start with three hardcoded questions through a fake LLM and grow that into a full package, step by step.

By the end of this lab, on your own machine you'll have:

- A proper Python package (`src/pipeline/`) with separated concerns — logging is one module, config is another, persistence is another.
- A pipeline that reads **20 real questions from a CSV** and outputs typed `Answer` objects with cost and retry metadata.
- **Two Pydantic models you author yourself** — `Settings` (typed runtime config with `Field(...)` constraints) and `RunSummary` (per-execution rollup). The starter file only *uses* Pydantic via the pre-built `Question` / `Answer` from `fake_llm.py`; here you author your own.
- Calls to the **real OpenAI API** (not the fake stand-in), still parallel, still retried with backoff, still logged.
- A `runs` table and an `answers` table in **SQLite**, queryable from a small CLI script.
- A documented use of an **AI coding assistant** for one small improvement, with the verification workflow written down.

We start with a starter file (`pipeline_starter.py` from the cohort repo) and grow it into a small package: driven by typed config, fed by a CSV, summarising each run, persisting to a queryable store, and crossing the boundary from fake to real LLM. Each step *extends* the previous — no rewrites.

## Learning outcomes

By finishing this lab you can:

1. Structure a small Python package with separated modules.
2. **Define your own Pydantic models** with `Field(...)` constraints.
3. Run async calls in **batched parallel** with retries and exponential backoff.
4. Emit machine-readable JSON logs.
5. Persist results to a real database and query them.
6. Use an AI coding assistant safely, with a verification habit you can describe.

---

## Before you start

You should already have:

- Your **W1 capstone repo** cloned in Vocareum (the one with `src/hello_llm.py` and `docs/adr/0001-capstone-framing.md`).
- The cohort repo accessible somewhere on your machine — it has the **W2 starter file** (`pipeline_starter.py`), the **fake-LLM module** (`fake_llm.py`), and the **20-question CSV** (`questions.csv`).

Confirm your tools:

```bash
python --version       # expect Python 3.11.x
python -c "import os; print('OPENAI_API_KEY present:', bool(os.getenv('OPENAI_API_KEY')))"
```

**Step 0 below** confirms your tooling is ready and locates the cohort-repo files we'll copy in. Do that step first — even a 60-second check saves time later.

---

## How to pace this across the two W2 days

W2 is delivered over **Saturday + Sunday** (Day 1 + Day 2). The four lab steps map naturally onto the two evenings:

| When | Steps | Approx time | What you'll have done |
|------|-------|-------------|-----------------------|
| **Saturday evening** (after Day 1) | Step 1 — Project skeleton + typed `Settings` model | ~30 min | First Pydantic model authored · `src/pipeline/{logging_config,settings}.py` in place · `Settings` validated and ready |
| **Sunday + Monday + Tuesday** (after Day 2) | Step 2 — Build `pipeline.py` from the starter · Step 3 — Extend the pipeline · Step 4 — SQLite persistence · Step 5 — Coding-assistant exercise | ~220 min total | `pipeline.py` built from the starter (4 TODOs filled in) · Full async batch pipeline running against the real API · two Pydantic models authored (`Settings` + `RunSummary`) · `results.db` with two tables · `docs/lab2-assistant-notes.md` |

If you can only do the lab in one sitting, all four steps work as a single ~3-hour chunk after Day 2. **The whole lab is due before Wednesday** so you're not racing into W3.

---

## How to read this guide

Every sub-step in this lab follows the same seven-beat shape, so you always know where you are:

1. **What we're doing & why** — the goal of this sub-step in plain language, before any code.
2. **Where we are now** — what your files / pipeline look like at the *start* of this sub-step.
3. **What we're about to change** — described in words first, so you know the plan.
4. **Make the change** — describes what to build or edit (file paths, function shapes, behaviour, constraints) and points to the pre-uploaded reference file for the exact code.
5. **Run it** — the literal command to execute.
6. **What you should see** — the literal expected output, with `←` arrows pointing at teaching moments.
7. **What just happened** — 2–4 sentences discussing what the output means and why it matters.

Plus, where useful:

- **Watch for** — two or three common ways this sub-step fails, and what each failure looks like.
- **Narrate** — a literal line worth saying out loud (or thinking, if you're self-paced) at the teaching moment.
- **If this fails live** — a one-line fallback for the riskier sub-steps so the lesson still lands when the world doesn't cooperate.

Sub-step headers also carry a **mode tag** — `💻 Self-paced` (do on your own) or `📺 Live demo` (the instructor walks the cohort through this one on screen — same content, same lab guide) — plus a time estimate.

---

## Reference files in your environment

All of these are **pre-uploaded** into your lab environment under `<cohort-repo>/week2/`. This guide tells you when to consult each.

### Starter files (under `<cohort-repo>/week2/starter/`)

| Path | What it is | Used in |
|---|---|---|
| `pipeline_starter.py` | Skeleton with three `NotImplementedError` stubs and one commented TODO. Copy to `src/pipeline/pipeline.py` to start work. | Step 2a |
| `fake_llm.py` | Fake-LLM module with `Question`, `Answer`, `fake_ask_llm`, `FakeLLMError`. Copy as-is. | Step 2a |
| `data/questions.csv` | The 20 lab questions. Copy to `data/questions.csv`. | Step 1a |
| `pydantic_demo.py` | Standalone demo of Pydantic v2 model construction + validation. | Optional reading before Step 1c |

### Reference files (under `<cohort-repo>/week2/reference/`)

These are the completed versions of every module you write in the lab. Workflow rule: **edit your working file; read the reference when you need to check the exact form**. Don't copy verbatim — typing the shape yourself is part of how it lands.

| Path | What it is | Reference for |
|---|---|---|
| `requirements.txt` | Four pinned dependencies | Step 1b |
| `logging_config.py` | Completed `JsonFormatter` + `get_logger()` module | Step 1c |
| `settings.py` | Completed `Settings` + `RunSummary` Pydantic models | Steps 1c, 3d |
| `pipeline_reference.py` | Completed `pipeline.py` (all four stubs filled, JSON logging, Settings + logging wired, CSV loader, batched runner, summarise_run, real-API branch) | Steps 2b–2e, 3a–3f |
| `store.py` | Completed SQLite persistence module | Step 4a |
| `query_results.py` | Completed query CLI | Step 4c |

If any reference file is missing from your environment, flag it to your instructor before proceeding — every sub-step assumes the matching reference is reachable.

---

## Step 0 — Where we begin · 💻 Self-paced · 5 min

Before we touch anything, let's confirm your environment is ready and locate the three cohort-repo files we'll copy in over the next two steps.

### Step 0a — Confirm your environment + cohort repo files

**1. What we're doing & why.** This lab assumes Python 3.11, an OPENAI_API_KEY in your environment, and three files from the cohort repo — `pipeline_starter.py`, `fake_llm.py`, and `questions.csv`. We'll verify all of these in 60 seconds so the rest of the lab doesn't surprise you with a missing-file error.

**2. Where we are now.** You finished Day 2 of W2. Your W1 capstone repo is still where you left it (with `src/hello_llm.py` and `docs/adr/`). The cohort repo is cloned somewhere on your machine — let's find out where.

**3. What we're about to do.** Three checks: Python version, OpenAI key, and locate the three cohort-repo files.

**4. Make the check.**

```bash
python --version
python -c "import os; print('OPENAI_API_KEY present:', bool(os.getenv('OPENAI_API_KEY')))"
```

Then find the three cohort-repo files. The location depends on where you cloned the cohort repo — common locations are `~/cohort-repo/week2/`, `~/agentic-ai-cohort/week2/`, or similar. Find them with:

```bash
find ~ -name "pipeline_starter.py" 2>/dev/null
find ~ -name "fake_llm.py"         2>/dev/null
find ~ -name "questions.csv"       2>/dev/null
```

**5. Run it — confirm all four checks pass.**

(All four commands together; copy each output.)

**6. What you should see.**

```
Python 3.11.x                                                     ← any 3.11.x is fine
OPENAI_API_KEY present: True                                      ← Vocareum has this set already

/home/.../cohort-repo/week2/starter/pipeline_starter.py            ← path to the starter
/home/.../cohort-repo/week2/starter/fake_llm.py                    ← path to the fake LLM module
/home/.../cohort-repo/week2/starter/data/questions.csv             ← path to the 20-question CSV
```

**7. What just happened.** You've confirmed all three external dependencies are in place: the Python interpreter, the API key, and the three cohort-repo files we'll copy into your capstone repo over the next two steps. **Note the cohort-repo path** — you'll use it in Steps 1a (questions.csv) and 2a (the other two). If any check failed, see *Watch for* below.

**Watch for.**

- `Python 3.10.x` or `3.9.x` → ask the instructor about the Vocareum Python version, or use `python3.11` explicitly.
- `OPENAI_API_KEY present: False` → on Vocareum, open a fresh terminal. Off-Vocareum, you'll set up `.env` in Step 1d.
- `find` returns nothing → you haven't cloned the cohort repo. `git clone <cohort-repo-url> ~/cohort-repo` first.

---

## Step 1 — Project skeleton (~30 min) · *do after Day 1*

We turn the flat class files into a proper Python package and add the two pieces of infrastructure that the rest of the lab leans on: a JSON logger in its own module, and your first authored Pydantic model (`Settings`).

### Step 1a — Add the W2 directory layout · 💻 Self-paced · 5 min

**1. What we're doing & why.** A clean directory layout makes the rest of the lab obvious — every script knows where to find its inputs (CSV), outputs (JSON, DB), logs, and config. We're creating the structure your package will live in for the rest of W2.

**2. Where we are now.** Your repo has the W1 artefacts (`src/hello_llm.py`, `docs/adr/0001-capstone-framing.md`) but no W2 structure yet. No `src/pipeline/` subpackage, no `data/`, no `logs/`.

```
<your-capstone-repo>/
├── src/hello_llm.py          ← from W1
├── docs/adr/...              ← from W1
└── (other W1 artefacts)
```

**3. What we're about to change.** Three moves:

1. Create new directories: `src/pipeline/`, `data/`, `logs/`.
2. Create an empty `src/pipeline/__init__.py` (this turns the folder into a Python package).
3. Copy `questions.csv` from the cohort repo into `data/`. (We'll copy `pipeline_starter.py` and `fake_llm.py` in **Step 2a** — they belong with the build, not the skeleton.)

**4. Make the change.** From your repo root:

```bash
mkdir -p src/pipeline data logs
touch src/pipeline/__init__.py
```

Then copy the CSV (use the path you found in Step 0a):

```bash
cp <cohort-repo>/week2/starter/data/questions.csv  data/questions.csv
```

**5. Run it.**

```bash
ls src/pipeline/ && echo --- && head -3 data/questions.csv
```

**6. What you should see.**

```
__init__.py                                                       ← marks the folder as a Python package
---
text                                                              ← header row, single column
What is retrieval-augmented generation in one sentence?
Name three real-world uses of vector databases.
```

**7. What just happened.** Your repo now has a proper Python package at `src/pipeline/`, ready to grow into. The CSV that holds the 20 lab questions sits in `data/`. The empty `__init__.py` is the signal to Python that `src.pipeline` is an importable package — without it, the `from .settings import Settings` style of import we'll use throughout the lab wouldn't work. We deliberately *haven't* copied `pipeline_starter.py` yet — it lands in Step 2a alongside `fake_llm.py`, when we're ready to build.

**Watch for.**

- `cp: cannot stat '<cohort-repo>/...'` → the placeholder `<cohort-repo>` needs to be the real path on your machine. Use the path from Step 0a's `find` output.
- `ls: cannot access 'src/pipeline/'` → `mkdir -p` failed silently. Re-run from the repo root.

---

### Step 1b — Install dependencies · 💻 Self-paced · 3 min

**1. What we're doing & why.** Pin the exact versions of the libraries the lab uses, so the lab works the same on every machine in the cohort. We're being explicit about **Pydantic v2** — v1 syntax differs and would break the lab.

**2. Where we are now.** Your repo has no `requirements.txt` yet. The Pydantic and OpenAI packages may or may not be installed at the right versions on your machine.

**3. What we're about to change.** Two moves:

1. Create a `requirements.txt` at the repo root with four lines.
2. Run `pip install -r requirements.txt`.

**4. Make the change.** Create `requirements.txt` at the repo root listing four pinned dependencies — `openai>=1.0`, `pydantic>=2.0`, `python-dotenv>=1.0`, and `httpx>=0.27`. The reference is at `<cohort-repo>/week2/reference/requirements.txt`.

Then install:

```bash
pip install -r requirements.txt
```

**5. Run it — verify the versions.**

```bash
python -c "import openai, pydantic, dotenv, httpx; print('OK ·', 'pydantic', pydantic.VERSION)"
```

**6. What you should see.**

```
OK · pydantic 2.x.x      ← v2 is what the lab assumes; v1 syntax differs
```

**7. What just happened.** All four required packages import cleanly, and Pydantic specifically is v2 (the major version that introduced `Field(gt=...)` constraint syntax, `model_validate_json`, and `model_dump`). The lab uses v2 features throughout; if you somehow had v1 installed, almost everything would fail at construction.

**Watch for.**

- `error: externally-managed-environment` → add `--break-system-packages` (on Vocareum that's the right flag; locally, prefer a venv).
- Output starts with `pydantic 1.` → upgrade explicitly: `pip install --upgrade 'pydantic>=2.0'`.

---

### Step 1c — JSON logging in its own module + your first Pydantic model · 📺 Live demo · 15 min

**1. What we're doing & why.** Two pieces of infrastructure go in together — both will be imported by `pipeline_starter.py` when we drop it in Step 2a. First, a **dedicated logging module** (`logging_config.py`) with a JSON-formatted logger that writes to `logs/pipeline.log` — every script in the package shares one logger. Second, an **author-your-first-Pydantic-model exercise**: a `Settings` model (`settings.py`) capturing runtime configuration (batch size, fail rate, file paths) with type validation. After this step a bad config like `batch_size=0` gets caught at construction with a clear error, not three function calls later. You'll see that catch happen.

**2. Where we are now.** Your repo has the W1 artefacts, the `src/pipeline/` package skeleton from 1a, and the dependencies installed in 1b. Inside `src/pipeline/` there's only the empty `__init__.py` — no Python modules yet. The `pipeline_starter.py` we drop in Step 2a expects to import a configured logger and a typed `Settings` from sibling modules; we build those two sibling modules here, in 1c, *before* the starter lands. Doing it in this order keeps the starter file clean (no infrastructure glued onto it) and proves the package layout works before we add the main logic.

**3. What we're about to change.** Three moves:

1. **Create a new file** `src/pipeline/logging_config.py` and put the `JsonFormatter` in it, wrapped in a `get_logger()` helper that writes to **`logs/pipeline.log`** instead of stderr.
2. **Create a second new file** `src/pipeline/settings.py` and write a Pydantic `Settings` model with type-validated fields and `Field(...)` constraints.
3. We *don't* touch `pipeline.py` here — that file doesn't exist in your repo yet. It lands in **Step 2a** as a starter, and we wire `logging_config` + `Settings` into it in **Step 3a**.

**4a. Make the change — create `src/pipeline/logging_config.py`.** The completed module is at `<cohort-repo>/week2/reference/logging_config.py`. The module exposes two things:

- A **`JsonFormatter`** class extending `logging.Formatter`. Its `format(record)` method returns a JSON string with four fields: `ts` (epoch seconds rounded to 3 dp), `level` (the levelname), `msg` (the formatted message), `logger` (the logger name).
- A **`get_logger(name="pipeline", log_path="logs/pipeline.log")`** function that returns a configured `logging.Logger`. It sets `INFO` level, attaches a `FileHandler` writing to the given path (creating the `logs/` directory if missing), and guards against double-attaching handlers by checking `log.handlers` first.

Type the module yourself; consult the reference if stuck.

**Why this module is shaped this way:**

- `JsonFormatter` has **four fields** — timestamp, level, message, logger name. Enough to grep useful answers out of a log file later; not so much that every line becomes a wall.
- The setup is wrapped in a `get_logger()` function, so any module can `from .logging_config import get_logger` and get the *same* logger.
- We write to a **file** (`logs/pipeline.log`) rather than stderr — so logs persist between runs and you can `tail -f` or `grep` later.
- `if log.handlers: return log` guards against double-attaching handlers (which would print every log line twice if `get_logger()` were called more than once).
- The `mkdir(parents=True, exist_ok=True)` creates `logs/` on first run if you forgot.

**4b. Make the change — create `src/pipeline/settings.py`.** The completed module is at `<cohort-repo>/week2/reference/settings.py`. Define a single `Settings` class extending `pydantic.BaseModel` with seven fields:

| Field | Type | Default | Constraint |
|---|---|---|---|
| `questions_csv` | `Path` | `Path("data/questions.csv")` | — |
| `results_json` | `Path` | `Path("results.json")` | — |
| `results_db` | `Path` | `Path("results.db")` | — |
| `batch_size` | `int` | `Field(5, gt=0, le=20)` | `> 0` and `≤ 20` |
| `fail_rate` | `float` | `Field(0.0, ge=0.0, le=1.0)` | `0.0 ≤ x ≤ 1.0` |
| `model` | `str` | `"gpt-4o-mini"` | — |
| `use_fake` | `bool` | `True` | — |

The constraints are what make this a *typed* config rather than just a dict — `batch_size=0` raises `ValidationError` at construction, not three function calls later.

**Reading this model line by line:**

- `class Settings(BaseModel):` — Pydantic v2 syntax, same shape as the `Question` and `Answer` from `fake_llm.py`.
- `questions_csv: Path = Path("data/questions.csv")` — a path-typed field with a default. Pass a string and Pydantic converts it to a `Path` automatically.
- `batch_size: int = Field(5, gt=0, le=20)` — integer, default 5, must be **g**reater **t**han 0 and **l**ess than or **e**qual to 20. Violations raise `ValidationError` at construction.
- `fail_rate: float = Field(0.0, ge=0.0, le=1.0)` — float between 0.0 and 1.0 inclusive.
- `use_fake: bool = True` — default is the fake LLM. We flip this to `False` in Step 3f.

This is your **first Pydantic model authored from scratch**. The cohort's `fake_llm.py` ships pre-built `Question` / `Answer` models that you'll *use* later in the lab; here you *author* your own — and you'll write a second one (`RunSummary`) in Step 3d.

> **Narrate.** *"This is the first Pydantic model you've authored. The `Field(gt=0)` line isn't decorative — it's the difference between a bug at line 200 and a clear error at construction. Watch what happens when we try `batch_size=0`."*

**5. Run it — try to break the model on purpose.** From the repo root (not from inside `src/pipeline/`):

```bash
python -c "from src.pipeline.settings import Settings; Settings(batch_size=0)"
```

**6. What you should see.**

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
batch_size                                                  ← which field broke
  Input should be greater than 0   [type=greater_than,      ← which rule fired
   input_value=0, input_type=int]                           ← what you sent
```

**7. What just happened.** This is the *point* of authoring a typed `Settings` model. You tried to construct it with `batch_size=0`, which violates the `gt=0` constraint. Pydantic refused at construction time with a three-part error that names **which field broke**, **which rule fired**, and **what you sent**. Without the constraint, `batch_size=0` would silently propagate into `range(0, len(questions), 0)` and crash there with the cryptic `ValueError: range() arg 3 must not be zero` — and you'd spend ten minutes tracing the cause. With the constraint, you find it at line 1.

**5b. Run it — now construct it cleanly.**

```bash
python -c "from src.pipeline.settings import Settings; import json; print(json.dumps(Settings().model_dump(mode='json'), indent=2))"
```

**6b. What you should see.**

```
{
  "questions_csv": "data/questions.csv",                    ← typed Path, serialised to a string
  "results_json":  "results.json",
  "results_db":    "results.db",
  "batch_size": 5,                                          ← default, inside (0, 20]
  "fail_rate":  0.0,                                        ← default, inside [0.0, 1.0]
  "model":      "gpt-4o-mini",
  "use_fake":   true                                        ← we start on the fake; flip in Step 3f
}
```

**7b. What just happened.** No arguments → all defaults → all constraints satisfied → a typed object whose fields we know match their declared types. The `model_dump(mode='json')` call serialises `Path` objects back to strings so the output is JSON-friendly. Every `Settings()` call with no arguments will produce exactly this shape — same defaults, every run.

**Watch for.**

- `ModuleNotFoundError: No module named 'src'` → you're inside `src/pipeline/`. `cd` to the repo root.
- `PydanticUserError: Cannot generate a JsonSchema for ... Path` → Pydantic v1 is installed. `pip install --upgrade 'pydantic>=2.0'`.
- The `ValidationError` does **not** appear when you pass `batch_size=0` → you wrote `gt=-1` or omitted the constraint. Open `settings.py` and check the `Field(5, gt=0, le=20)` line.

---

### Step 1d — Smoke-test `Settings` + the logger together · 💻 Self-paced · 7 min

**1. What we're doing & why.** The two new files from Step 1c (`logging_config.py` and `settings.py`) need to play well together. A small smoke test confirms a typed `Settings` can be constructed *and* that `get_logger()` writes a JSON record into `logs/pipeline.log`. We also confirm the W1 secrets discipline (`.env` not tracked by git). We do **not** edit `pipeline.py` here — it doesn't exist yet. We'll build it in Step 2, and Step 3a is where Settings + logging get wired into it.

**2. Where we are now.** `src/pipeline/` has `__init__.py`, `logging_config.py`, and `settings.py`. No `pipeline.py` yet. The `logs/` directory exists but is empty.

**3. What we're about to do.** Two checks:

1. Run a one-shot Python snippet that imports `Settings` and `get_logger`, constructs each, and writes a smoke-test log line.
2. Confirm `.env` is gitignored (carries over from W1; we re-verify).

**4. Make the check — run the smoke test.**

```bash
python -c "
from src.pipeline.settings import Settings
from src.pipeline.logging_config import get_logger

s = Settings()
log = get_logger()
log.info(f'smoke test — settings: {s.model_dump(mode=\"json\")}')
print('OK — settings constructed, log line written')
"
```

**5. Run it — confirm the log file got the line.**

```bash
cat logs/pipeline.log
```

**6. What you should see.**

```
OK — settings constructed, log line written                       ← from the print()
                                                                  ← then the log file:
{"ts": 1717.034, "level": "INFO", "msg": "smoke test — settings: {\"questions_csv\": ..., \"use_fake\": true}", "logger": "pipeline"}
```

**7. What just happened.** The two halves of your infrastructure work together: `Settings()` constructs cleanly, `get_logger()` configures the JSON file logger, and `log.info(...)` writes a structured record into `logs/pipeline.log`. The `mkdir(parents=True, exist_ok=True)` inside `get_logger()` quietly created `logs/` if it didn't exist. Every later sub-step that uses these files (the entire Step 3, all of Step 4) leans on this contract.

**Confirm `.env` is gitignored:**

```bash
grep -q "^\.env$" .gitignore || echo ".env" >> .gitignore
git ls-files | grep -q "^\.env$" && echo "PROBLEM: .env tracked" || echo "OK: .env not tracked"
```

You should see `OK: .env not tracked`. If you see `PROBLEM`, run `git rm --cached .env && git commit -m "chore: stop tracking .env"`.

**Watch for.**

- `ModuleNotFoundError: No module named 'src'` → you're inside `src/pipeline/`. `cd` to the repo root.
- `logs/pipeline.log` is empty after the smoke test → `get_logger()` failed silently. Re-check `logging_config.py` against Step 1c.
- The log line is plain text (not JSON) → wrong formatter. Verify `JsonFormatter` is the one assigned to the handler.

### ✅ Checkpoint 1

```bash
git add src/pipeline data/questions.csv logs/ .gitignore requirements.txt
git commit -m "feat: W2 skeleton — typed Settings + JSON logger module"
```

You should now have:

- `src/pipeline/{__init__.py, logging_config.py, settings.py}` (no `pipeline.py` yet — Step 2 builds it)
- `data/questions.csv` with 20 rows
- `logs/pipeline.log` with one smoke-test INFO record
- `.env` not tracked by git
- `Settings()` validated; `get_logger()` writes to `logs/pipeline.log`

---

## Step 2 — Build `pipeline.py` from the starter (~60 min) · *do after Day 2*

In this step you turn the starter file (4 `NotImplementedError` TODOs) into a working async batch pipeline. Five sub-steps, each builds on the previous, each runs visibly before you move on.

### Step 2a — Drop in the starter · 💻 Self-paced · 5 min

**1. What we're doing & why.** Get `pipeline_starter.py` and `fake_llm.py` into your package and rename the starter to `pipeline.py`. The starter file has four `NotImplementedError` stubs that we'll fill in sequentially (2b → 2e). The package layout from Step 1 is the home for both files.

**2. Where we are now.** After Step 1, your `src/pipeline/` has `__init__.py`, `logging_config.py`, and `settings.py`. No `pipeline.py` yet — that's what we add now. The cohort repo has the starter waiting for you.

**3. What we're about to change.** Three moves:

1. Copy `pipeline_starter.py` from the cohort repo's `week2/starter/` folder into `src/pipeline/pipeline.py`.
2. Copy `fake_llm.py` from the same folder into `src/pipeline/fake_llm.py`.
3. Confirm the four stubs are intact — running the file will fail at the first stub.

**4. Make the change.** From your repo root (the path to the cohort repo depends on where you cloned it):

```bash
cp <cohort-repo>/week2/starter/pipeline_starter.py  src/pipeline/pipeline.py
cp <cohort-repo>/week2/starter/fake_llm.py          src/pipeline/fake_llm.py
```

Then update the one import line at the top of your new `src/pipeline/pipeline.py`. The starter has a flat import (`from fake_llm import Question, Answer, fake_ask_llm, FakeLLMError`) but we're in a package now, so prefix it with a leading dot to make it relative: `from .fake_llm import ...`.

**Confirm the four stubs are present.** Open `src/pipeline/pipeline.py` and check that there are three `raise NotImplementedError(...)` lines — one inside `ask_llm` (Step 2), one inside `ask_llm_with_retry` (Step 3), one inside `run_batch` (Step 4) — plus a commented-out TODO block near the middle of the file for Step 5 (JSON logging setup). These four markers correspond to sub-steps 2b, 2c, 2d, and 2e.

**5. Run it — confirm the file parses and the first stub fires.**

```bash
python -m src.pipeline.pipeline
```

**6. What you should see.**

```
Traceback (most recent call last):
  ...
NotImplementedError: Step 2 — call fake_ask_llm and return the Answer       ← first TODO fires
```

**7. What just happened.** The file parses, all the imports resolve, and execution reaches the first `NotImplementedError` exactly where we expect — inside `ask_llm`. The crash is *informative*: it tells you which step you're at and what you're meant to build. Over the next four sub-steps you'll fill these in one at a time, and the script will get further on each iteration.

**Watch for.**

- `ModuleNotFoundError: No module named 'src'` → you're inside `src/pipeline/`. `cd` to the repo root.
- `ImportError: attempted relative import with no known parent package` → use `python -m src.pipeline.pipeline` (with `-m`), not `python src/pipeline/pipeline.py`.
- `ImportError: cannot import name 'fake_ask_llm' from 'src.pipeline.fake_llm'` → you got the wrong `fake_llm.py` (maybe an older version). Re-copy from the cohort repo.

---

### Step 2b — Fill in `ask_llm` · 💻 Self-paced · 10 min

**1. What we're doing & why.** `ask_llm` is the *single-call* function — one question goes in, one `Answer` comes out. The fake LLM (`fake_ask_llm`) has the same shape as the real `AsyncOpenAI` client we'll swap in later, so the body is a one-line `await`. This sub-step is small on purpose — it gets the *first stub* working so you can verify the function does what you expect before stacking retry on top in 2c.

**2. Where we are now.** Your `src/pipeline/pipeline.py` has the four stubs from Step 2a. Running it crashes immediately inside `ask_llm` with `NotImplementedError: Step 2 — ...`.

**3. What we're about to change.** Replace the `raise NotImplementedError(...)` body of `ask_llm` with one line that awaits `fake_ask_llm` and returns its `Answer`.

**4. Make the change.** Open `src/pipeline/pipeline.py` and find the `ask_llm` function (it currently raises `NotImplementedError`). Replace its body with a single line: `return await fake_ask_llm(q, fail_rate=fail_rate)`. The completed reference is at `<cohort-repo>/week2/reference/pipeline_reference.py`.

**Reading the new body line by line:**

- `await fake_ask_llm(q, fail_rate=fail_rate)` — `fake_ask_llm` is async, so we need `await` to actually get the `Answer` back (without `await`, we'd get a coroutine *object*, not the result).
- `return` — return the `Answer` directly. The fake function already returns a Pydantic `Answer` model, so there's no parsing to do.
- We're **not** adding the `log.info(...)` line yet — the logger doesn't exist until Step 2e. The starter file has a TODO comment reminding us to come back.

The interface is intentional: the same signature works for the real `AsyncOpenAI` client in W2's later step (Step 3f). Only the *body* changes; everything that *calls* `ask_llm` stays unaware.

**5. Run it — call the function directly to confirm it works.**

```bash
python -c "
import asyncio
from src.pipeline.pipeline import ask_llm, Question
ans = asyncio.run(ask_llm(Question(text='What is RAG in one sentence?')))
print('type:', type(ans).__name__)
print('text:', ans.text[:80])
print('cost:', ans.cost_usd)
print('retries:', ans.retries)
"
```

**6. What you should see.**

```
type: Answer                                                       ← Pydantic Answer model, as expected
text: RAG combines retrieval over a document corpus with an LLM...  ← canned answer from fake_llm
cost: 0.0001                                                       ← per-call cost (set inside fake_ask_llm)
retries: 0                                                         ← no retries yet — that's 2c's job
```

**7. What just happened.** Your first stub is filled. `ask_llm(q)` now actually makes a call (against the fake) and returns a typed `Answer`. The function signature is locked in: any code that takes a `Question` and gets back an `Answer` doesn't need to know whether the call hit the fake or the real API. This is the abstraction that makes the W2-to-rest-of-programme transition smooth — same shape, swappable bodies.

**Watch for.**

- `TypeError: object NoneType can't be used in 'await' expression` → you forgot `return` or used `=` instead of `await`. Re-check the body.
- The `text:` line shows `None` → you have `return None` somewhere; check there's only one `return` line.
- `RuntimeWarning: coroutine 'fake_ask_llm' was never awaited` → you wrote `fake_ask_llm(q, ...)` without `await`. Add `await` before the call.

---

### Step 2c — Fill in `ask_llm_with_retry` · 💻 Self-paced · 15 min

**1. What we're doing & why.** Real calls fail. The retry wrapper is the difference between "one transient blip and the whole batch dies" and "one transient blip and the system recovers silently." We wrap `ask_llm` with a `for` loop that tries up to `tries` times, sleeping `1, 2, 4, …` seconds between attempts (the **exponential backoff** pattern from Topic 3). This is the most code-dense sub-step of Step 2 — take your time.

**2. Where we are now.** `ask_llm` works (from 2b). `ask_llm_with_retry` still has its `NotImplementedError("Step 3 — ...")` stub. If you tried to run with `fail_rate=0.5`, you'd see roughly half the calls bubble up as `FakeLLMError` because nothing is catching them.

**3. What we're about to change.** Replace the `raise NotImplementedError(...)` body of `ask_llm_with_retry` with a retry loop. The starter file's commented-out TODO shows the shape — your job is to make it a real loop.

**4. Make the change.** Find `ask_llm_with_retry` in `src/pipeline/pipeline.py` and replace its body. The completed reference is at `<cohort-repo>/week2/reference/pipeline_reference.py`. The shape:

- A `for attempt in range(tries):` loop where `tries` defaults to 3.
- Inside the loop: `try`/`except Exception`. The `try` block awaits `ask_llm(q, fail_rate=fail_rate)`, sets `ans.retries = attempt` (the count of retries that happened), and returns the answer.
- The `except` block: if this was the *final* attempt (`attempt == tries - 1`), re-raise so the caller sees the failure. Otherwise sleep `2 ** attempt` seconds (so 1 s then 2 s then 4 s) and let the loop iterate.
- A defensive `raise RuntimeError("unreachable")` after the loop so the type checker is satisfied.

**Reading the body line by line:**

- `for attempt in range(tries):` — loop up to `tries` times (default 3). `attempt` takes the values 0, 1, 2.
- `try:` … `except Exception:` — wrap the call in a try/except. If `ask_llm` raises (`FakeLLMError` from the fake, or any real exception from the real API), we catch it and decide whether to retry.
- `ans = await ask_llm(q, fail_rate=fail_rate)` — the actual call, with `await` because `ask_llm` is async.
- `ans.retries = attempt` — record how many times we *retried* (0 on first success, 1 if we succeeded on the second try, etc.). This is the field that feeds the W2-onwards retry-rate metric.
- `if attempt == tries - 1: raise` — if this was the *final* attempt, give up: re-raise the exception so the caller can decide what to do. (Without this, the loop would silently exit and we'd return `None`.)
- `await asyncio.sleep(2 ** attempt)` — exponential backoff. On attempt 0 (= first failure), sleep 1 s. On attempt 1, sleep 2 s. On attempt 2 we don't sleep — we just raise (caught above). The `**` is Python's exponent operator.
- `raise RuntimeError("unreachable")` — defensive line so the type-checker doesn't complain that the function might return without a value. With the `tries >= 1` loop above, this line is genuinely unreachable.

> **Narrate.** *"The `2 ** attempt` is doing real work. First retry waits 1 second; second retry waits 2 seconds. That backoff is what stops a hammering retry loop from making the underlying failure worse. We'll see this fire visibly in 2e when we run with `fail_rate=0.4`."*

**5. Run it — try a clean call first, then a guaranteed-fail call.**

```bash
python -c "
import asyncio
from src.pipeline.pipeline import ask_llm_with_retry, Question

# Clean — should succeed on attempt 0, no retries
ans = asyncio.run(ask_llm_with_retry(Question(text='What is RAG?')))
print('clean:    retries =', ans.retries)

# Always-fail — should retry twice (3 attempts total) and then raise
try:
    asyncio.run(ask_llm_with_retry(Question(text='What is RAG?'), fail_rate=1.0))
except Exception as e:
    print('lossy:    raised after 3 attempts:', type(e).__name__)
"
```

**6. What you should see.**

```
clean:    retries = 0                                       ← first try succeeded, no retries
lossy:    raised after 3 attempts: FakeLLMError             ← all 3 attempts failed → re-raised
```

Bonus: if you wait the few seconds the lossy run takes to complete, you'll *feel* the 1 s + 2 s backoff in real time.

**7. What just happened.** The retry wrapper works. With `fail_rate=0.0` (the default), the call succeeds first try and `retries = 0`. With `fail_rate=1.0` (always fails), it tries three times — sleeping 1 s, then 2 s — and then gives up by re-raising. Notice the structural choice: this function doesn't *swallow* failures; if all retries fail, the caller sees the exception. That's deliberate — *silent* failures are the worst kind of failure.

**Watch for.**

- `clean: retries = 2` (or any non-zero value on a clean run) → your `ans.retries = attempt` line is in the wrong place. It needs to be *before* the `return ans`.
- The lossy test prints `lossy: raised after 3 attempts: TypeError` (or similar) → the loop is exiting without raising. Check the `if attempt == tries - 1: raise` line — `tries - 1` (not `tries`).
- The lossy run finishes in <1 s → you forgot `await asyncio.sleep(...)`. The backoff has to be `await`-ed.

---

### Step 2d — Fill in `run_batch` · 💻 Self-paced · 10 min

**1. What we're doing & why.** `run_batch` fires *every* question in the list in parallel via `asyncio.gather`. This is the **gather pattern** from Topic 3 (slide 18 in your deck). One line of code, but it's the difference between 20 sequential ~1-second calls (~20 s) and 20 parallel ones (~1.5 s). Run it once and you'll see the speed-up viscerally.

**2. Where we are now.** `ask_llm` and `ask_llm_with_retry` both work (from 2b and 2c). `run_batch` still has its `NotImplementedError("Step 4 — ...")` stub.

**3. What we're about to change.** Replace the `raise NotImplementedError(...)` body of `run_batch` with two lines that build the tasks list and `await asyncio.gather(*tasks)`.

**4. Make the change.** Find `run_batch` in `src/pipeline/pipeline.py` and replace its body. The completed reference is at `<cohort-repo>/week2/reference/pipeline_reference.py`. Two lines:

- Build a list comprehension `tasks = [ask_llm_with_retry(q, fail_rate=fail_rate) for q in questions]`. These are coroutine *objects* — they're not running yet.
- `return await asyncio.gather(*tasks)`. The `*tasks` unpacks the list as positional arguments because `gather` takes one task per argument, not a list. The `await` returns when *all of them* are done; results are returned in input order.

**Reading the body line by line:**

- `tasks = [ask_llm_with_retry(q, fail_rate=fail_rate) for q in questions]` — a list comprehension that builds one coroutine per question. **Important:** these coroutines are not running yet — they're objects, not results.
- `await asyncio.gather(*tasks)` — *now* they all start. `gather` schedules every coroutine on the event loop concurrently. The `await` returns when *all of them* are done. The `*tasks` unpacks the list as positional arguments (because `gather` takes one task per argument, not a list).
- Result type: `list[Answer]`. `gather` preserves *input order* — `result[0]` corresponds to `questions[0]`, even though the calls didn't finish in order.

**5. Run it — fire 3 questions in parallel.**

```bash
python -c "
import asyncio, time
from src.pipeline.pipeline import run_batch, Question

questions = [
    Question(text='What is RAG?'),
    Question(text='Name three uses of vector databases.'),
    Question(text='Why might an LLM hallucinate?'),
]
t0 = time.time()
answers = asyncio.run(run_batch(questions))
elapsed = time.time() - t0
print(f'wall-clock: {elapsed:.2f}s')
for a in answers:
    print(f'- {a.text[:60]}')
"
```

**6. What you should see.**

```
wall-clock: 1.4s                                           ← all 3 parallel, ~longest single call
- RAG combines retrieval over a document corpus...          ← input order preserved
- Vector databases power semantic search, RAG context...
- LLMs hallucinate when they produce confident text...
```

**7. What just happened.** Three calls. Each one takes ~0.3–1.5 s on the fake. **Sequentially**, that'd be ~3 s. **In parallel** via `gather`, it's ~1.4 s — bounded by the *slowest single call*, not the sum. The order of the answers matches the input order even though the calls almost certainly didn't *finish* in input order. That's `gather`'s guarantee: parallel execution, ordered results. This one-line abstraction is doing the heavy concurrency lifting for the rest of the lab.

**Watch for.**

- `wall-clock: 3.5s` → calls running sequentially. Check that there's a `*` before `tasks` in the `gather` call.
- `TypeError: object of type 'list_iterator' has no len()` → you wrote `asyncio.gather(tasks)` instead of `asyncio.gather(*tasks)`.
- Output is in a random order → your list comprehension is constructing coroutines correctly but you're sorting or shuffling somewhere; check your code matches the snippet exactly.

---

### Step 2e — Add JSON logging + run twice (clean + lossy) · 💻 Self-paced · 20 min

**1. What we're doing & why.** Fill in the last TODO — the **JSON-formatted structured logger** — and run the pipeline twice: once clean (`fail_rate=0.0`), once lossy (`fail_rate=0.4`). The first run shows parallelism. The second run shows the retry pattern firing visibly. This is the moment all three concurrency patterns (gather + batching-via-list + retry) work *together* as a pipeline.

**2. Where we are now.** `ask_llm`, `ask_llm_with_retry`, `run_batch` all work. The `__main__` block runs them on three sample questions. But there's no logging yet — output to the terminal is just the final `print(f"- {a.text[:80]}")` line. The Step 5 TODO at the bottom of the starter file is still commented out.

**3. What we're about to change.** Two edits:

1. **Fill in the Step 5 TODO** — add a `JsonFormatter` class, a `log` logger configured with a `StreamHandler`.
2. **Add `log.info(...)` calls** inside `ask_llm` and `ask_llm_with_retry` so every call (and every retry) emits a JSON record.

Then run twice — clean first, then lossy — and inspect the log output.

**4. Make the change.** Open `src/pipeline/pipeline.py`. Find the *Step 5* commented-out TODO block near the middle of the file. Replace it with the JSON-logging setup, which has two parts:

1. A `JsonFormatter` class extending `logging.Formatter`. Its `format(record)` method returns a JSON string with three fields here (ts, level, msg) — the same shape as `logging_config.py`, but inline this time. We'll replace this duplication with the imported `get_logger` in Step 3a.
2. Below the class: `log = logging.getLogger("pipeline")`, then `log.setLevel(logging.INFO)`, then attach a `StreamHandler` with `JsonFormatter()` as its formatter.

The completed Step 5 block is in `<cohort-repo>/week2/reference/pipeline_reference.py` (search for `# ---------- Step 5`).

**Reading the logger setup:**

- `class JsonFormatter(logging.Formatter)` — a custom log formatter. Python's `logging` module calls `format(record)` on every log message; our subclass returns JSON instead of plain text.
- `json.dumps({"ts": ..., "level": ..., "msg": ...})` — emit a dict with three fields. `record.levelname` is `"INFO"` / `"WARNING"` / etc. `record.getMessage()` is whatever was passed to `log.info(...)`.
- `log = logging.getLogger("pipeline")` — get *the* `pipeline` logger (Python keeps one per name, so this is the same `log` everywhere).
- `log.setLevel(logging.INFO)` — log INFO and above. (DEBUG would be too noisy.)
- `_handler = logging.StreamHandler()` — write to stderr by default. (We'll redirect to a file in Step 3a.)
- `_handler.setFormatter(JsonFormatter())` — use our custom formatter for this handler.
- `log.addHandler(_handler)` — wire the handler into the logger.

Now **add a `log.info(...)` call inside `ask_llm`** so every call emits a record. Find your `ask_llm` (which you wrote in 2b). Two edits to the body:

1. Capture the result of `await fake_ask_llm(...)` into a variable (`ans` is conventional) instead of returning it directly.
2. Add `log.info(f"asked: {q.text[:40]}")` before the `return ans`.

The `[:40]` truncation keeps the log line readable. Reference: `<cohort-repo>/week2/reference/pipeline_reference.py`.

And **add a `log.warning(...)` call inside `ask_llm_with_retry`** so we can see retries happening. Find your `ask_llm_with_retry` (which you wrote in 2c). Two edits to the `except` clause:

1. Bind the exception with `as exc` (`except Exception as exc:`).
2. Just before the `await asyncio.sleep(...)` line, add `log.warning(f"retry {attempt + 1} for: {q.text[:40]} ({exc})")`. The `attempt + 1` makes the log human-friendly ("retry 1" rather than "retry 0").

Reference: `<cohort-repo>/week2/reference/pipeline_reference.py`.

**5. Run it — first a clean run.**

```bash
python -m src.pipeline.pipeline 2>&1 | head -10
```

(`2>&1` redirects stderr to stdout so we can pipe the JSON logs.)

**6. What you should see (clean).**

```
{"ts": 1717.034, "level": "INFO", "msg": "asked: What is RAG in one sentence?"}              ← call 1
{"ts": 1717.041, "level": "INFO", "msg": "asked: Name three uses of vector databases."}      ← 7 ms later → parallel
{"ts": 1717.043, "level": "INFO", "msg": "asked: Why might an LLM hallucinate?"}             ← all 3 firing close together

3 answers in 1.36s

- RAG combines retrieval over a document corpus with an LLM, so answers...
- Vector databases power semantic search, RAG context retrieval, and...
- LLMs hallucinate when they produce confident text that isn't grounded...
```

**7. What just happened (clean).** Three log lines, three answers, all in ~1.4 seconds. The log line timestamps tell the parallelism story: the three `INFO` records are within ~10 ms of each other, even though each call took 0.3–1.5 s. The three concurrency patterns from Topic 3 are now stacking visibly — `gather` (parallel inside the batch), Pydantic models (the typed `Question` / `Answer` flow), and the retry wrapper (idle right now because nothing failed).

**5b. Run it — now lossy (force retries to fire).**

```bash
python -m src.pipeline.pipeline 0.4 2>&1 | head -20
```

**6b. What you should see (lossy — randomness, but typical output).**

```
{"ts": 1718.105, "level": "WARNING", "msg": "retry 1 for: Why might an LLM... (simulated...)"}    ← retry 1
{"ts": 1718.114, "level": "INFO",    "msg": "asked: What is RAG..."}                              ← this one succeeded first try
{"ts": 1718.916, "level": "WARNING", "msg": "retry 1 for: Name three uses... (simulated...)"}     ← retry 1, 800 ms later (different call)
{"ts": 1719.117, "level": "INFO",    "msg": "asked: Why might an LLM..."}                         ← retry succeeded
{"ts": 1719.928, "level": "INFO",    "msg": "asked: Name three uses..."}                          ← retry succeeded

3 answers in 2.82s                                                ← slower because of the backoff sleeps
```

**7b. What just happened (lossy).** Each call had ~40% chance of failing on the fake. The retry wrapper caught each `FakeLLMError`, logged a `WARNING`, slept 1 s, tried again. **All three answers still arrived** — the pipeline is reliable in the face of failure. Wall-clock is now ~2.8 s instead of ~1.4 s; the difference is the backoff sleeps. Look at the timestamp deltas — the 1-s gap between a `retry 1` line and the next `INFO` for that question is the `await asyncio.sleep(2 ** 0)` doing real work.

> **Narrate.** *"The clean run showed parallelism. The lossy run showed reliability. Same code, same Pydantic shapes, same gather — just a different fail rate on the fake. This is what 'engineering on top of one LLM call' means: parallelism, retries, backoff, structured logs. None of it changes the call itself."*

### ✅ Checkpoint 2

```bash
git add src/pipeline/pipeline.py src/pipeline/fake_llm.py
git commit -m "feat: pipeline.py — async batch with retry + JSON logging"
```

You should now have:

- `src/pipeline/pipeline.py` with all four TODOs filled in.
- A clean run producing 3 answers in ~1.4 s with 3 JSON log lines.
- A lossy run (`fail_rate=0.4`) producing 3 answers in ~2.8 s with visible `retry 1` / `retry 2` `WARNING` lines.
- Both `ask_llm` and `ask_llm_with_retry` emitting structured logs.

> **You've built the pipeline.** What's next is *extending* it — typed `Settings` driving the run, a CSV of 20 questions, batched fan-out, a `RunSummary`, persistence to SQLite, and the real OpenAI API.

---

## Step 3 — Extend the async batch pipeline (~90 min) · *do after Day 2*

This is the long step. Six sub-steps stack: wire `Settings` + the JSON logger module into `pipeline.py`, read questions from CSV, run them in *batched* parallel, author a second Pydantic model for the run summary, write everything to `results.json`, and flip from the fake LLM to the real OpenAI API.

### Step 3a — Wire `Settings` + `logging_config` into `pipeline.py` · 💻 Self-paced · 10 min

**1. What we're doing & why.** Your `pipeline.py` from Step 2 has its own inline `JsonFormatter` and reads `fail_rate` from `sys.argv[1]`. Both work — but neither uses the typed `Settings` from Step 1c or the shared `logging_config` module. This sub-step swaps both in, so the rest of Step 3 can lean on `settings.batch_size`, `settings.fail_rate`, etc. without surprises.

**2. Where we are now.** Your `src/pipeline/pipeline.py` (from Step 2) has:

- A `JsonFormatter` class defined **inline** near the middle of the file.
- A `log = logging.getLogger("pipeline")` / `StreamHandler` setup directly in this file.
- An `__main__` block reading `fail_rate = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0`.

**3. What we're about to change.** Three edits:

1. **Delete** the inline `JsonFormatter` class + the four lines that set up the logger (we built `logging_config.py` in Step 1c — use it).
2. **Add** two import lines: `from .logging_config import get_logger` and `from .settings import Settings`. Then `log = get_logger()` (so existing `log.info` calls still work).
3. **Replace** the `__main__` block — drop `sys.argv` parsing; construct `Settings()` instead.

**4. Make the change.**

First, **delete** the inline logging block (the `JsonFormatter` class and the four-line `StreamHandler` setup). It's at the section commented `# ---------- Step 5: structured (JSON) logging ----------`.

Then **add three lines at the top of `pipeline.py`** (after the existing imports): a `from .logging_config import get_logger` import, a `from .settings import Settings` import, and a `log = get_logger()` call to bind the logger to the same name your earlier `log.info(...)` and `log.warning(...)` calls already use.

Then **replace the `__main__` block** with one that:

1. Constructs `settings = Settings()` (no `sys.argv` parsing).
2. Logs the resolved config with `log.info(f"config: {settings.model_dump(mode='json')}")` — so any past run is trivially answerable for *"what was running when this ran?"*.
3. Keeps the three sample questions for now (CSV loading lands in Step 3b).
4. Calls `asyncio.run(run_batch(sample, fail_rate=settings.fail_rate))` — note `fail_rate` now comes from `settings`, not `sys.argv`.
5. Prints each answer's first 80 characters.

Reference: `<cohort-repo>/week2/reference/pipeline_reference.py`.

**What changed:**

- The `sys.argv[1]` parse is gone — `settings.fail_rate` replaces it (default 0.0 from the model).
- Logs now go to a **file** (`logs/pipeline.log`) via `get_logger()` — not stderr.
- `log.info(f"config: {settings.model_dump(...)}")` writes the *whole resolved config* as one log line at run start, so "what was running when this ran?" is trivially answerable for any past run.

**5. Run it.**

```bash
python -m src.pipeline.pipeline
tail -n 4 logs/pipeline.log
```

**6. What you should see.**

Console:

```
- RAG combines retrieval over a document corpus with an LLM, so answers...        ← canned fake answer
- Vector databases power semantic search, RAG context retrieval, and...
- LLMs hallucinate when they produce confident text that isn't grounded...
```

Log file (last 4 lines):

```
{"ts": ..., "level": "INFO", "msg": "config: {\"questions_csv\": ..., \"use_fake\": true}"}    ← whole Settings, one line
{"ts": ..., "level": "INFO", "msg": "asked: What is RAG in one sentence?"}
{"ts": ..., "level": "INFO", "msg": "asked: Name three uses of vector databases."}
{"ts": ..., "level": "INFO", "msg": "asked: Why might an LLM hallucinate?"}
```

**7. What just happened.** Same behaviour as Step 2 (three parallel calls, three answers) — but now driven by typed config and logged to a file. Bad runtime values (`batch_size=0`, `fail_rate=2.0`) are now impossible because `Settings()` validates at construction. The pipeline is now ready to grow — Steps 3b–3f add CSV loading, batching, `RunSummary`, and the real API on top of this wiring.

**Watch for.**

- `ImportError: attempted relative import with no known parent package` → use `python -m src.pipeline.pipeline` (with `-m`).
- `logs/pipeline.log` is empty → you didn't delete the old inline `StreamHandler` block; it's still hijacking the logger. Find and delete it.
- `NameError: name 'Settings' is not defined` → check the import line at the top of `pipeline.py`.

---

### Step 3b — Read questions from the CSV · 💻 Self-paced · 12 min

**1. What we're doing & why.** Real pipelines don't hardcode their inputs. The class build had three sample questions baked into `__main__`; that's pedagogically fine but useless for any real workload. We're adding a `load_questions()` function that reads the 20 questions from `data/questions.csv` and returns them as `Question` Pydantic objects — the exact same model your async pipeline already accepts.

**2. Where we are now.** Your `src/pipeline/pipeline.py` (after Step 3a) has three hardcoded `Question(text=...)` entries in `__main__` — the `sample` list. The rest of the file has no awareness of any CSV.

**3. What we're about to change.** Two moves:

1. **Add** a `load_questions()` function near the top of `pipeline.py` that opens the CSV and returns `list[Question]`.
2. We *don't* update `__main__` yet — that happens in Step 3c when we add the batched runner.

**4. Make the change — add to `src/pipeline/pipeline.py`.**

At the top of `pipeline.py`, add two imports if they aren't already there: `import csv` and `from pathlib import Path`.

Then add a `load_questions(path: str | Path = "data/questions.csv") -> list[Question]` function. A good place is right after the imports, before `ask_llm`. The body:

- Open the file with `newline=""` and `encoding="utf-8"`.
- Read all rows into a list via `csv.DictReader(f)`.
- Return a list comprehension building one `Question(text=row["text"])` per row, skipping any rows where `row.get("text")` is falsy (handles blank lines and missing fields).

Reference: `<cohort-repo>/week2/reference/pipeline_reference.py`.

**Reading this function line by line:**

- `def load_questions(path: ...) -> list[Question]:` — takes a path (string or `Path`), returns a list of `Question` Pydantic models.
- `csv.DictReader(f)` parses each row into a dict keyed by the header (so `row["text"]` gets the value in the `text` column).
- `[Question(text=row["text"]) for row in rows if row.get("text")]` constructs a `Question` for each non-empty row. The `if row.get("text")` skips blank lines.

Note: this function returns the *same* `Question` Pydantic objects that `ask_llm` already accepts. We're just changing the *source* of the list, not the shape.

**5. Run it — quick standalone test.**

```bash
python -c "from src.pipeline.pipeline import load_questions; qs = load_questions(); print(len(qs)); print(qs[0]); print(type(qs[0]).__name__)"
```

**6. What you should see.**

```
20                                                                       ← every row in the CSV loaded
text='What is retrieval-augmented generation in one sentence?'           ← first row as a Pydantic model
Question                                                                 ← the exact same model your pipeline expects
```

**7. What just happened.** The CSV is now a typed input source. `load_questions()` parsed 20 rows and turned each into a `Question(text=...)` Pydantic object — the exact same shape the rest of your pipeline already accepts. You didn't change a single line of `ask_llm`, `ask_llm_with_retry`, or `run_batch`; you only changed where the questions *come from*. This is what good engineering looks like: when the data source changes, the rest of the pipeline doesn't care, because the *contract* (a list of `Question` objects) is preserved.

**Watch for.**

- `FileNotFoundError: 'data/questions.csv'` → you ran from inside `src/`; cd back to the repo root.
- `KeyError: 'text'` → the CSV column header is something other than `text`. Either fix the CSV or rename the column lookup in code.
- `len(qs)` is 0 → empty file or wrong path. `head -3 data/questions.csv` to check.

---

### Step 3c — Batched fan-out with `gather` · 📺 Live demo · 18 min

**1. What we're doing & why.** Your class build used `asyncio.gather` over *all* questions at once. That worked for three; for 20, 200, or 2,000 questions it'd hit rate limits, eat memory, and make you a noisy neighbour. We add `run_in_batches()` — same `gather`, but in chunks of `batch_size` with a gentle pause between chunks. This is the **batching pattern** from Topic 3, applied for real for the first time.

**2. Where we are now.** Your `pipeline.py` (after Step 3b) has `run_batch` from Step 2d — one big `asyncio.gather` over *all* questions at once. That's fine for 3 questions, bad for 20+: it'd hit rate limits and make you a noisy neighbour.

**3. What we're about to change.** Two moves:

1. **Add** a new `run_in_batches()` function that breaks the questions into chunks of 5 and gathers each chunk separately.
2. **Update** the `__main__` block to load 20 questions from the CSV and call `run_in_batches`.

We leave `run_batch` in place (it's still used by your fall-back scripts and the W1 quizzes reference it).

**4. Make the change — add to `src/pipeline/pipeline.py`.**

Add a new `run_in_batches(questions, batch_size=5, fail_rate=0.0)` async function right after `run_batch`. Reference: `<cohort-repo>/week2/reference/pipeline_reference.py`. The shape:

- Initialise an empty `out: list[Answer] = []`.
- Loop with `for i in range(0, len(questions), batch_size)` — strides of `batch_size` through the questions list.
- Inside the loop: slice the chunk with `questions[i : i + batch_size]`. Log the batch number and chunk size with `log.info`. Run `await asyncio.gather(*(ask_llm_with_retry(q, fail_rate=fail_rate) for q in chunk))` — fires all 5 in parallel and waits for all 5 to finish. Extend `out` with the batch's answers.
- After each batch, `await asyncio.sleep(0.1)` — a 100 ms pause to give the API breathing room.
- After the loop, `return out`.

**Reading this function line by line:**

- `for i in range(0, len(questions), batch_size):` — walks through the questions list in strides of `batch_size`. For 20 questions and `batch_size=5`, this runs the loop 4 times: i=0, 5, 10, 15.
- `chunk = questions[i : i + batch_size]` — slices out 5 questions at a time.
- `log.info(f"batch {i // batch_size + 1}: ...")` — writes a log line at the start of each batch so we can see the boundaries.
- `await asyncio.gather(*(...))` — fires all 5 questions in the chunk in parallel. Returns when *all 5* are done.
- `out.extend(batch_answers)` — appends this batch's answers to the running list.
- `await asyncio.sleep(0.1)` — 100 ms pause between batches. Tiny on its own; matters when you scale to thousands.

Then **update the `__main__` block** so it:

1. Constructs `settings = Settings()`.
2. Calls `load_questions(settings.questions_csv)` (from Step 3b) instead of the hardcoded `sample` list.
3. Logs how many questions were loaded with `log.info(f"loaded {len(questions)} questions")`.
4. Records `started = time.time()` before the run.
5. Calls `asyncio.run(run_in_batches(questions, batch_size=settings.batch_size, fail_rate=settings.fail_rate))` (note: `batch_size` is now sourced from `settings`, not hardcoded).
6. Computes `elapsed` and logs `done: N answers in M.MMs`.

Reference: `<cohort-repo>/week2/reference/pipeline_reference.py`.

> **Narrate.** *"Look at the timestamps in the log. The first five calls fire within milliseconds of each other — that's parallelism inside the batch. Then a gentle 100 ms pause, then the next five. That's parallelism with backpressure — gentle on the API, fast on the cohort."*

**5. Run it — clean fake run.**

```bash
python -m src.pipeline.pipeline
tail -n 30 logs/pipeline.log
```

**6. What you should see (annotated):**

```
{"ts": 1717.005, "msg": "loaded 20 questions"}                       ← Settings + CSV worked
{"ts": 1717.007, "msg": "batch 1: 5 questions"}                      ← first batch starts
{"ts": 1717.015, "msg": "asked: What is retrieval-augmented..."}
{"ts": 1717.018, "msg": "asked: Name three real-world uses..."}      ← 3 ms after the first → parallel
{"ts": 1717.020, "msg": "asked: Why might an LLM produce..."}
{"ts": 1717.022, "msg": "asked: What is a Pydantic BaseModel..."}
{"ts": 1717.024, "msg": "asked: Explain async and await..."}         ← all five inside ~20 ms
{"ts": 1718.156, "msg": "batch 2: 5 questions"}                      ← gentle 100 ms pause between batches
{"ts": 1718.164, "msg": "asked: ..."}
...
{"ts": 1721.420, "msg": "done: 20 answers in 4.42s"}                 ← 20 questions, ~4.4 s (sync would be ~16 s)
```

**7. What just happened.** Twenty questions through a real batched pipeline. The log lines tell the whole story: each batch of 5 fires its calls within ~20 ms of each other (that's parallel inside the batch), then a brief pause before the next batch (that's backpressure between batches). The whole thing finished in ~4.4 seconds wall-clock; sync, it'd be ~16 seconds. This is the moment where the *three concurrency patterns from Topic 3* stack visibly: `gather` (parallel inside a chunk), batching (chunks of 5), and retry (still inside `ask_llm_with_retry`, ready for when we add failures in Step 3e).

**Watch for.**

- Pipeline takes ~15 s for 20 questions → you forgot `await` somewhere, so it's running serially. Scan for any `ask_llm(...)` without `await` in front.
- `'NoneType' object is not iterable` → `load_questions` returned `None`; check the CSV path and column header.
- All five answers print in completion order rather than input order → that's a bug elsewhere; `gather` always returns in input order.

---

### Step 3d — Author your second Pydantic model — `RunSummary` · 💻 Self-paced · 13 min

**1. What we're doing & why.** Where `Settings` captured *config* (the same every run), `RunSummary` captures *runtime data* (different every run): how long the run took, how many retries happened, what the cost was. This is your second authored Pydantic model. It's the seed of the KPI scoreboard we build from W6 onward — every run gets a one-row summary, persisted to a `runs` table next.

**2. Where we are now.** Your `settings.py` has just one class — `Settings`. Your `pipeline.py` runs and prints, but doesn't produce any structured artefact summarising the run.

**3. What we're about to change.** Two moves:

1. **Append** a second class — `RunSummary` — to `settings.py`. Same file (these are both data shapes).
2. **Add** a `summarise_run()` helper to `pipeline.py` that constructs a `RunSummary` from the list of answers plus wall-clock data.

**4a. Make the change — append a `RunSummary` class to `src/pipeline/settings.py`** (after the existing `Settings` class). Reference: `<cohort-repo>/week2/reference/settings.py`. Eight fields:

| Field | Type | Constraint |
|---|---|---|
| `started_at` | `float` | — (unix timestamp from `time.time()`) |
| `elapsed_seconds` | `float` | `Field(ge=0.0)` — non-negative |
| `n_questions` | `int` | `Field(ge=0)` |
| `n_succeeded` | `int` | `Field(ge=0)` |
| `n_retries_total` | `int` | `Field(ge=0)` |
| `total_cost_usd` | `float` | `Field(ge=0.0)` |
| `fail_rate` | `float` | `Field(ge=0.0, le=1.0)` |
| `use_fake` | `bool` | — |

The constraints aren't decorative — `Field(ge=0)` on `n_retries_total` means if you sum the wrong field and end up negative, Pydantic refuses to construct.

**Reading this model:**

- `started_at: float` — unix timestamp at run start (from `time.time()`).
- `elapsed_seconds: float = Field(ge=0.0)` — wall-clock duration. Constraint: non-negative.
- `n_questions: int = Field(ge=0)` — number of questions processed.
- `n_succeeded: int = Field(ge=0)` — answers that came back successfully.
- `n_retries_total: int = Field(ge=0)` — sum of retries across all answers.
- `total_cost_usd: float = Field(ge=0.0)` — sum of per-answer cost. Constraint guards against accidental negatives.
- `fail_rate: float = Field(ge=0.0, le=1.0)` — what fail rate the pipeline ran at (for the fake LLM path).
- `use_fake: bool` — true if this run used the fake LLM; false if real API.

These constraints aren't decorative either — `Field(ge=0)` on `n_retries_total` means if you somehow summed the wrong field and got a negative, Pydantic refuses to construct.

**4b. Make the change — add to `src/pipeline/pipeline.py`** (a good place is right after `load_questions` or `run_in_batches`). Reference: `<cohort-repo>/week2/reference/pipeline_reference.py`.

Two edits:

1. **Update the existing import line** for `settings` to also pull in `RunSummary`: `from .settings import Settings, RunSummary`.
2. **Add a `summarise_run` function** with this signature: `summarise_run(answers: list[Answer], *, started_at: float, elapsed: float, fail_rate: float, use_fake: bool) -> RunSummary`. The body constructs and returns a `RunSummary` with `n_questions` and `n_succeeded` both equal to `len(answers)`, `n_retries_total` equal to `sum(a.retries for a in answers)`, `total_cost_usd` equal to `sum(a.cost_usd for a in answers)`, and the other fields passed through from the call.

The `*` in the signature forces every parameter after `answers` to be keyword-only — so callers must write `summarise_run(answers, started_at=..., elapsed=..., fail_rate=..., use_fake=...)` rather than relying on positional order. Safer for a function with 5 parameters.

**What this helper does:** takes the list of `Answer` objects your pipeline already produces, plus a few pieces of wall-clock data, and builds a single `RunSummary` Pydantic object. The `sum(a.retries for a in answers)` and `sum(a.cost_usd for a in answers)` rolls up per-answer data into per-run totals.

**5. Run it — try a bad value first.**

```bash
python -c "from src.pipeline.settings import RunSummary; RunSummary(started_at=0, elapsed_seconds=-1, n_questions=0, n_succeeded=0, n_retries_total=0, total_cost_usd=0, fail_rate=0, use_fake=True)"
```

**6. What you should see.**

```
ValidationError: 1 validation error for RunSummary
elapsed_seconds
  Input should be greater than or equal to 0  [type=greater_than_equal,
  input_value=-1, input_type=int]                              ← the negative caught at the door
```

**7. What just happened.** Same teaching moment as the `Settings` constraint, on a different field. `elapsed_seconds=-1` makes no sense (you can't have a negative duration), and the `Field(ge=0.0)` constraint refused it at construction. If you accidentally subtracted `started - completed` instead of `completed - started`, this catches the bug at the door rather than letting a nonsense summary land in your database.

**5b. Run it — now a clean construction.**

```bash
python -c "
from src.pipeline.settings import RunSummary
import json
s = RunSummary(started_at=1717.0, elapsed_seconds=4.42, n_questions=20, n_succeeded=20, n_retries_total=0, total_cost_usd=0.002, fail_rate=0.0, use_fake=True)
print(json.dumps(s.model_dump(), indent=2))
"
```

**6b. What you should see.**

```
{
  "started_at": 1717.0,
  "elapsed_seconds": 4.42,                                     ← real wall-clock you'll record
  "n_questions": 20,
  "n_succeeded": 20,
  "n_retries_total": 0,                                        ← non-zero when fail_rate > 0
  "total_cost_usd": 0.002,                                     ← honest aggregate of per-answer cost
  "fail_rate": 0.0,
  "use_fake": true
}
```

**7b. What just happened.** Two Pydantic models authored, two different roles. `Settings` (config — same every run) and `RunSummary` (observation — different every run). One field on `RunSummary` is `fail_rate` — that's *the fail_rate we ran with*, copied across from `Settings`. The two models *talk to each other* through these shared fields; we'll use that in Step 4 when we persist runs to SQLite and you want to ask "which run had the highest fail_rate?"

**Watch for.**

- `ValidationError: ... should be greater than or equal to 0` → you summed costs wrong (got a negative). Check the field name.
- `TypeError: missing N required positional arguments` → you forgot one of the required fields in the constructor call.

---

### Step 3e — Run end-to-end with the fake LLM and inspect · 📺 Live demo · 17 min

**1. What we're doing & why.** Wire `summarise_run` into `__main__` so every run produces a `RunSummary`, and write the whole thing to `results.json` (summary block + 20 answers). Then we run it twice — first clean, then with `fail_rate=0.3` — so we *see* the retry pattern firing in the log.

**2. Where we are now.** Your `pipeline.py` runs 20 questions in batched parallel and prints them. There's no `results.json`, no summary capture, and `fail_rate` is hard-coded to whatever `Settings.fail_rate` defaults to (0.0).

**3. What we're about to change.** One concrete edit:

1. **Replace** the `__main__` block to build a `RunSummary`, log it, and write `{"summary": ..., "answers": [...]}` to `results.json`.

Then we'll run twice — clean once, lossy once — to see retries.

> **If this fails live.** *Permission or path issue on `results.json`? Override it: `settings.results_json = Path("/tmp/results.json")` at the top of `__main__`. The lesson stands; the file location doesn't matter.*

**4. Make the change — replace `__main__` in `src/pipeline/pipeline.py`.** Reference: `<cohort-repo>/week2/reference/pipeline_reference.py`. The new `__main__` block does six things, in order:

1. **Construct** `settings = Settings()`.
2. **Load** questions with `load_questions(settings.questions_csv)` and log how many were loaded.
3. **Time the run** — capture `started = time.time()` before, `elapsed = time.time() - started` after `asyncio.run(run_in_batches(...))`.
4. **Build the summary** by calling `summarise_run(answers, started_at=started, elapsed=elapsed, fail_rate=settings.fail_rate, use_fake=settings.use_fake)`.
5. **Log the summary** with `log.info(f"summary: {summary.model_dump_json()}")` — one JSON line capturing the entire run shape.
6. **Write `results.json`** with `settings.results_json.write_text(...)`. The JSON body has two top-level keys: `summary` (from `summary.model_dump(mode="json")`) and `answers` (a list comprehension `[a.model_dump() for a in answers]`). End with a `print(f"wrote {len(answers)} answers to {settings.results_json} in {elapsed:.2f}s")`.

`model_dump(mode="json")` (rather than just `model_dump()`) converts `Path` objects to strings, which makes the result JSON-serialisable without manual conversions.

**What changed:**

- After the `run_in_batches` call, we call `summarise_run` to build the `RunSummary`.
- `log.info(f"summary: {summary.model_dump_json()}")` writes the whole summary as one JSON log line — easy to grep later.
- The big write to `results.json` packages the summary *and* the 20 answers into one JSON file: `{"summary": {...}, "answers": [...]}`.

**5. Run it — clean run first.**

```bash
python -m src.pipeline.pipeline
head -20 results.json
```

**6. What you should see.**

Console:

```
wrote 20 answers to results.json in 4.42s     ← parallel speedup
```

`results.json` (first 20 lines):

```
{
  "summary": {
    "started_at": 1717.34,
    "elapsed_seconds": 4.42,                                   ← parallel speedup
    "n_questions": 20,
    "n_succeeded": 20,
    "n_retries_total": 0,                                      ← clean run, no retries
    "total_cost_usd": 0.002,
    "fail_rate": 0.0,
    "use_fake": true
  },
  "answers": [
    {
      "question": "What is retrieval-augmented generation in one sentence?",
      "text": "RAG combines retrieval over a document corpus with an LLM...",
      "cost_usd": 0.0001,
      "retries": 0
    },
```

**7. What just happened.** The pipeline now produces a *structured artefact* — `results.json` contains both the run's summary (one `RunSummary` row) and all 20 answers. This is what good engineering looks like: the run is no longer ephemeral; it's a *thing* you can read, diff, share, and feed into a downstream analyser. `n_retries_total: 0` confirms the clean fake run didn't hit any retries — exactly as expected at `fail_rate=0.0`.

**5b. Now force some failures.** Edit `src/pipeline/settings.py` — change the default value on the `fail_rate` field from `0.0` to `0.3` (keep the same `ge=0.0, le=1.0` constraints). Then run again:

```bash
python -m src.pipeline.pipeline
grep -E '"(WARN|level.: .WARN)' logs/pipeline.log | tail -5
```

**6b. What you should see (filtered to retries).**

```
{"ts": 1718.105, "level": "WARNING", "msg": "retry 1 for: Why might an LLM..."}   ← first retry, 1 s backoff
{"ts": 1718.918, "level": "WARNING", "msg": "retry 1 for: Explain async and..."}
{"ts": 1719.224, "level": "WARNING", "msg": "retry 2 for: Why might an LLM..."}   ← second retry, 2 s backoff
{"ts": 1721.450, "level": "INFO",    "msg": "asked: Why might an LLM..."}         ← eventual success
{"ts": 1721.520, "level": "INFO",    "msg": "done: 20 answers in 6.83s"}          ← slower because of retries
```

Check the summary captures the retries:

```bash
python -c "import json; print(json.load(open('results.json'))['summary'])"
```

```
{'started_at': ..., 'elapsed_seconds': 6.83, ..., 'n_retries_total': 3, ...}     ← retries counted in the summary
```

**7b. What just happened.** This is the **single most important moment of W2** for understanding the retry pattern. With `fail_rate=0.3`, ~30% of fake calls raise `FakeLLMError`. Your retry wrapper caught each failure, slept 1 second (`2 ** 0`), retried — if it still failed, slept 2 seconds (`2 ** 1`), retried again. The log shows that backoff *visibly* — look at the timestamp deltas between the `retry 1` and `retry 2` lines. The whole pipeline took ~6.8 s instead of ~4.4 s (the retries cost wall-clock time), but every answer still came through. `n_retries_total: 3` in the summary captures this honestly — it's the data we'll feed into reliability metrics from W6.

**Restore `fail_rate=0.0`** in `settings.py` before moving on.

**Watch for.**

- `n_retries_total` is 0 even with `fail_rate=0.3` → randomness; run again, you'll see retries on most runs.
- Pipeline crashes with `FakeLLMError` after retries → fail rate is too high; 0.3 × 0.3 × 0.3 ≈ 3% chance of three misses in a row. Drop the rate to 0.2 or up `tries` to 5.
- `KeyError: 'summary'` when reading `results.json` → an exception interrupted the write; check the log for the first `ERROR`.

---

### Step 3f — Flip `use_fake` — call the real API · 📺 Live demo · 20 min

**1. What we're doing & why.** This is the moment that makes the whole programme real: crossing the boundary from the fake LLM stand-in to a real OpenAI API call. The architecture doesn't change — same `Settings`, same `RunSummary`, same retry, same logs. You just flip one boolean. That's the engineering point: a good abstraction makes the swap one line.

**2. Where we are now.** Your `pipeline.py` always calls the fake LLM (`fake_ask_llm`). Your `Settings.use_fake` field defaults to `True` but no code branches on it yet.

**3. What we're about to change.** Two moves:

1. **In `settings.py`**, change the default `use_fake: bool = True` to `use_fake: bool = False`.
2. **At the top of `pipeline.py`**, branch on `settings.use_fake` to import *either* `fake_ask_llm` *or* the real `AsyncOpenAI` client. Then update `ask_llm` to call whichever path was selected.

> **Narrate.** *"We've built the engineering against a fake — fast, free, predictable. Same Settings, same Pydantic models, same retry, same logs. Now we flip one boolean and talk to a real model that costs real money. The architecture doesn't change."*

> **If this fails live.** *Real API hiccup, key issue, or rate limit mid-class? Flip `use_fake` back to `True` and continue. The engineering lesson stands; the real-API switch is the last 30 seconds and learners can do it at home.*

**4a. Make the change — edit `src/pipeline/settings.py`.** Change the default of the `use_fake` field from `True` to `False`. (The reference for the completed settings.py is at `<cohort-repo>/week2/reference/settings.py`.)

**4b. Make the change — edit the top of `src/pipeline/pipeline.py`.** Replace the existing `from .fake_llm import ...` line with a branched import that decides at module-load time which path to use. Reference: `<cohort-repo>/week2/reference/pipeline_reference.py`. The structure:

1. **Import settings** — keep the existing `from .settings import Settings, RunSummary` line.
2. **Construct a module-level settings instance** named `_settings_for_import = Settings()`. The leading underscore signals "private to this module".
3. **Branch on `_settings_for_import.use_fake`**:
   - If `True` — keep the existing `from .fake_llm import Question, Answer, fake_ask_llm, FakeLLMError`.
   - If `False` — import `load_dotenv` from `dotenv`, `AsyncOpenAI` from `openai`, and `BaseModel` from `pydantic`. Call `load_dotenv()` to pick up `OPENAI_API_KEY` from `.env`. Instantiate `_client = AsyncOpenAI()`. Define inline `Question(BaseModel)` with one field `text: str`, and `Answer(BaseModel)` with four fields: `question: str`, `text: str`, `cost_usd: float`, `retries: int = 0`. Defining them inline (rather than importing from `fake_llm.py`) keeps the real-API path self-contained.

The `_settings_for_import` is read again later in `ask_llm` — that's the point: one source of truth on which path is active.

**4c. Make the change — update `ask_llm` in `src/pipeline/pipeline.py`** to branch on `_settings_for_import.use_fake`. Reference: `<cohort-repo>/week2/reference/pipeline_reference.py`. The new body:

- **If `use_fake` is True** — same one-liner from Step 2b: `ans = await fake_ask_llm(q, fail_rate=fail_rate)`.
- **Else (real API)** — `await _client.chat.completions.create(model=_settings_for_import.model, messages=[{"role": "user", "content": q.text}])`. Then construct an `Answer` from the response: `question=q.text`, `text=resp.choices[0].message.content`, `cost_usd=0.0001` (placeholder — real cost from `response.usage` lands in W25).
- **After the branch** — keep the `log.info(f"asked: {q.text[:40]}")` line and `return ans`.

The `fail_rate` parameter is only used by the fake path; the real API has its own error modes and doesn't need synthetic ones.

**What changed:** `ask_llm` now has two branches. The `use_fake=True` path is the fake-LLM mode from earlier in this lab. The `use_fake=False` path is real — it calls `AsyncOpenAI`'s chat completion endpoint and wraps the response in your `Answer` model. The *rest* of the pipeline (`ask_llm_with_retry`, `run_in_batches`, `summarise_run`, persistence) doesn't know or care which path ran.

**5. Run it — sanity check on 3 questions first.** Real API calls cost real (tiny) money. Before running on all 20, trim the CSV to its first three rows OR copy them to a separate `data/questions_small.csv` and point `Settings.questions_csv` at that. Then:

```bash
python -m src.pipeline.pipeline
python -c "import json; d=json.load(open('results.json')); print(d['answers'][0]['text'][:200])"
```

**6. What you should see.**

```
wrote 3 answers to results.json in 2.10s     ← real API latency, ~700 ms per call in parallel

RAG, or Retrieval-Augmented Generation, is an approach that combines a       ← genuine model response
retrieval mechanism with a generative model, allowing the model to use         (not "(simulated answer)" any more)
external knowledge from a corpus to produce more accurate, grounded outputs.
```

**7. What just happened.** Same pipeline. Same Pydantic models. Same retry. Same logging. Same `results.json` structure. **Just talking to a real model now.** The answer is a real GPT-4o-mini response, not a canned string. The cost was a fraction of a cent. This is the moment `Settings.use_fake` earned its keep — *one boolean flip* and we're in production posture. If we'd hard-coded the fake path everywhere, this swap would have been a refactor; the abstraction makes it a config change.

**5b. Restore the full CSV and run all 20.**

```bash
python -m src.pipeline.pipeline
```

**6b. What you should see.**

```
wrote 20 answers to results.json in 3-8s     ← real API timing, varies
```

`results.json` summary now shows real numbers from the real API.

**7b. What just happened.** Twenty real LLM calls, in batches of 5, in parallel, with retry-on-failure (none expected from the real API on a clean network), all logged, all persisted. This is the W2 deliverable.

> **Cost reality check.** Twenty `gpt-4o-mini` calls cost a fraction of a cent. If you want to iterate on engineering changes without burning calls, flip `use_fake` back to `True` while debugging — that's exactly the workflow.

**Watch for.**

- `openai.AuthenticationError` → key not in env. On Vocareum, open a fresh terminal. Off-Vocareum, `.env` should have `OPENAI_API_KEY=...` and `load_dotenv()` is being called.
- `openai.RateLimitError` → `batch_size` is too high for your account. Drop to 3 in `Settings` and try again.
- All 20 calls take 30+ seconds → either the API is slow today, or `run_in_batches` is awaiting per call instead of using `gather`. Check Step 3c.

### ✅ Checkpoint 3

```bash
git add src/pipeline/pipeline.py src/pipeline/settings.py results.json logs/pipeline.log
git commit -m "feat: batched async pipeline + Settings + RunSummary; real API"
```

You should now have:

- Pipeline reads 20 questions from CSV, runs in batches of 5, retries on failure, logs every call.
- `results.json` contains a `summary` object (RunSummary fields) plus 20 `answers`, from the real API.
- `pipeline.py` is driven by a typed `Settings` instance; bad config is rejected at construction.
- Two authored Pydantic models in `settings.py`: `Settings` and `RunSummary`.

---

## Step 4 — Add SQLite persistence (~50 min) · *do after Day 2*

JSON is fine for one run. For analytics — *"which run had the most retries?", "show me all answers about RAG"* — we want a real table.

### Step 4a — Author the store module · 💻 Self-paced · 15 min

**1. What we're doing & why.** Create `store.py` with two tables (`runs` for `RunSummary` rows, `answers` for `Answer` rows tagged with `run_id`) and three small functions that write to them. SQLite is the simplest thing that works at this scale — built into Python, no server, one file on disk. Same pattern we'll reuse in W7 for document metadata.

**2. Where we are now.** Your `src/pipeline/` has `__init__.py`, `fake_llm.py`, `logging_config.py`, `pipeline.py`, `settings.py`. No persistence layer yet.

**3. What we're about to change.** Create one new file — `src/pipeline/store.py` — with:

- A SQL `SCHEMA` defining two tables (`runs` and `answers` with a foreign key).
- `connect(path)` — opens a SQLite connection, creates the tables if needed.
- `write_run(con, summary)` — inserts one row into `runs`, returns the new `rowid` for FK use.
- `write_answers(con, run_id, answers)` — bulk-inserts all answers tagged with the given `run_id`.

**4. Make the change — create `src/pipeline/store.py`.** Reference: `<cohort-repo>/week2/reference/store.py`. The module has four pieces:

1. **Imports.** `sqlite3`, `time`, `Path` from `pathlib`, `Iterable` from `typing`. Plus the package's own `Answer` (from `.pipeline`) and `RunSummary` (from `.settings`).

2. **`SCHEMA` — a multi-statement SQL string** defining two tables with `CREATE TABLE IF NOT EXISTS`. The `runs` table has 9 columns: `id` (autoincrement PK), `started_at` (REAL), `elapsed_seconds` (REAL), `n_questions` (INTEGER), `n_succeeded` (INTEGER), `n_retries_total` (INTEGER), `total_cost_usd` (REAL), `fail_rate` (REAL), `use_fake` (INTEGER — SQLite has no native bool, so 0/1). The `answers` table has 7 columns: `id` (autoincrement PK), `run_id` (INTEGER, with a `FOREIGN KEY` to `runs(id)`), `question` (TEXT), `answer` (TEXT), `cost_usd` (REAL), `retries` (INTEGER DEFAULT 0), `ts` (REAL).

3. **`connect(path="results.db") -> sqlite3.Connection`** — opens the connection, runs `SCHEMA` via `executescript`, commits, returns the connection.

4. **`write_run(con, summary) -> int`** — parameterised `INSERT INTO runs (...) VALUES (?, ?, ...)`, with `1 if summary.use_fake else 0` for the bool. Commits. Returns `cur.lastrowid` (the new run's PK — caller needs this for `write_answers`).

5. **`write_answers(con, run_id, answers) -> int`** — builds a list of tuples `(run_id, a.question, a.text, a.cost_usd, a.retries, ts)` and inserts them all via `con.executemany(...)`. Commits. Returns `len(rows)`.

`?` parameter placeholders rather than f-strings prevent SQL injection. `executemany` is much faster than 20 separate `INSERT` statements.

**Reading this file:**

- `SCHEMA` is a multi-statement SQL string; `con.executescript(SCHEMA)` runs the whole thing. The `IF NOT EXISTS` clauses mean it's safe to call `connect()` multiple times.
- `runs` table: one row per pipeline execution. Columns mirror `RunSummary` fields one-for-one. `use_fake` is stored as an integer (0/1) because SQLite has no native bool.
- `answers` table: one row per LLM call. The `run_id` column ties each answer back to its run via the `FOREIGN KEY` declaration.
- `write_run` uses parameterised SQL (`?` placeholders) — no string concatenation, so no SQL injection risk.
- `write_answers` uses `executemany` for bulk insert — much faster than 20 separate `INSERT` statements.

**5. Run it — quick standalone test that the tables get created.**

```bash
python -c "
from src.pipeline.store import connect
con = connect('test.db')
print(con.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall())
"
rm -f test.db
```

**6. What you should see.**

```
[('runs',), ('answers',)]                                   ← both tables created
```

**7. What just happened.** `connect('test.db')` created a fresh `test.db` file on disk, ran the `SCHEMA` (which created both tables), and committed. `sqlite_master` is SQLite's internal catalogue — querying it confirms our two tables exist. The whole persistence layer is one file, ~80 lines, no server needed. We deleted `test.db` because it was just a smoke test; the real persistence lands in Step 4b.

**Watch for.**

- `sqlite3.OperationalError: no such column: ...` → schema typo; drop the db file and re-run (SQLite caches schema in the file).
- `cannot import name 'Answer' from ... pipeline` → check `pipeline.py` defines (or imports) `Answer` at module scope. After Step 3f it's defined in both branches of the `if _settings_for_import.use_fake:` block.

---

### Step 4b — Wire `store` into the pipeline and persist the run · 💻 Self-paced · 10 min

**1. What we're doing & why.** Take the `RunSummary` and `Answer` list your pipeline already produces, and persist them to SQLite at the end of every run. Three lines of new code in `__main__`. From now on, every execution leaves a trail in `results.db` that you can query.

**2. Where we are now.** `store.py` has the schema and writers. `pipeline.py`'s `__main__` builds `summary` and writes `results.json`, but doesn't touch the database.

**3. What we're about to change.** One edit:

1. **Add** at the end of `__main__` in `pipeline.py`: import `connect`, `write_run`, `write_answers` from `store`, then write the run + the answers.

**4. Make the change — add four lines at the end of `__main__` in `src/pipeline/pipeline.py`** (after the `results.json` write). Reference: `<cohort-repo>/week2/reference/pipeline_reference.py`. The lines:

1. An **inside-`__main__` import**: `from .store import connect, write_run, write_answers`. (Why inside `__main__` and not at the top of the file: `store.py` imports `Answer` from `pipeline.py`; importing `store` at the top would cause a circular import. Deferring it to `__main__` runs the import after `pipeline.py` has fully loaded.)
2. A `with connect(settings.results_db) as con:` context — auto-closes the connection.
3. Inside the `with`: `run_id = write_run(con, summary)` to insert the run row and capture its `id`. Then `n = write_answers(con, run_id, answers)` to bulk-insert all 20 answers tagged with that `run_id`.
4. A `log.info(f"persisted run {run_id} with {n} answers to {settings.results_db}")` line for the run log.

**5. Run it.**

```bash
python -m src.pipeline.pipeline
python -c "
import sqlite3
con = sqlite3.connect('results.db')
print('runs:')
for r in con.execute('SELECT id, n_questions, n_retries_total, total_cost_usd, fail_rate, use_fake FROM runs'):
    print(' ', r)
print('answers per run:')
for r in con.execute('SELECT run_id, COUNT(*) FROM answers GROUP BY run_id'):
    print(' ', r)
"
```

**6. What you should see.**

```
runs:
  (1, 20, 0, 0.002, 0.0, 0)                                  ← one row per run; use_fake=0 means real API
answers per run:
  (1, 20)                                                    ← 20 answers tied to run_id=1
```

**7. What just happened.** Your pipeline now has a real persistence layer. After each run, `results.db` contains one new row in `runs` (the `RunSummary` snapshot) and 20 new rows in `answers` (each tagged with `run_id` = whatever `lastrowid` came back from `write_run`). The foreign-key relationship means you can join: *for this run, what answers came back, and what were their per-call retry counts?* This is the seed of the KPI dashboard from W6.

**Watch for.**

- `sqlite3.IntegrityError: NOT NULL constraint failed: answers.run_id` → you called `write_answers` before `write_run`, or didn't capture the returned `run_id`. Order matters.
- Two runs appear after one execution → you're calling `write_run` twice (once for testing, once in main). Check for stray test calls.

---

### Step 4c — A small query script · 📺 Live demo · 15 min

**1. What we're doing & why.** Persistence is only useful if it's queryable. We add `query_results.py` — a small CLI that lists recent runs and filters answers by substring. This is the first "analytics surface" on your pipeline data and the seed of the KPI dashboard.

**2. Where we are now.** You have data in `results.db` but the only way to read it is `sqlite3` command-line or `python -c "import sqlite3; ..."` — fine for debugging, not for daily use.

**3. What we're about to change.** Create one new file — `src/pipeline/query_results.py` — with two view functions and a `main()` that dispatches based on CLI args.

**4. Make the change — create `src/pipeline/query_results.py`.** Reference: `<cohort-repo>/week2/reference/query_results.py`. The module exposes:

1. **A module docstring** with three usage examples — `--runs` to list runs, no args to show all answers, a substring pattern to filter answers.

2. **`show_runs(con)`** — prints a header row (`id`, `started`, `questions`, `retries`, `cost_usd`, `fail`, `fake`) with fixed-width formatting, then loops over `con.execute("SELECT id, started_at, n_questions, n_retries_total, total_cost_usd, fail_rate, use_fake FROM runs ORDER BY id DESC")`, printing each row with column-aligned `f"{row[0]:>4}  {row[1]:>12.1f}  ..."` formatting.

3. **`search_answers(con, pattern)`** — runs a `SELECT id, run_id, retries, question, answer FROM answers WHERE question LIKE ? ORDER BY id` query with `(f"%{pattern}%",)` as the bound parameter (substring match anywhere). Loops over the rows printing each as `[#id run=run_id retries=retries] question → answer[:140]`.

4. **`main()`** — opens `sqlite3.connect("results.db")`, then dispatches: if `sys.argv[1] == "--runs"`, call `show_runs`; otherwise use `sys.argv[1]` (or empty string) as the search pattern and call `search_answers`.

5. **An `if __name__ == "__main__": main()` line** to make the file runnable via `python -m src.pipeline.query_results`.

Parameterised SQL (`?` placeholders) again — no string concatenation, no injection.

**Reading this file:**

- `show_runs` formats the `runs` table as a fixed-width table — one row per execution.
- `search_answers` does a `LIKE` query over the `question` column with `%pattern%` (substring match anywhere). The `(f"%{pattern}%",)` is a parameterised query — no SQL injection.
- `main` dispatches: if `--runs` was passed, show runs; otherwise search answers by the first arg (or empty string = match all).

**5. Run it — list runs first.**

```bash
python -m src.pipeline.query_results --runs
```

**6. What you should see.**

```
  id       started   questions   retries    cost_usd    fail  fake
   1       1717.6          20         0      0.0020    0.00     0           ← real API run from Step 3f
```

**5b. Then a substring search.**

```bash
python -m src.pipeline.query_results RAG
```

**6b. What you should see.**

```
[#1 run=1 retries=0] What is retrieval-augmented generation in one sentence?
   → Retrieval-Augmented Generation is an approach that combines a retrieval...     ← from the real API
```

**7. What just happened.** You can now ask analytical questions about your pipeline's history. `--runs` is the *operations* view ("how did each execution go?"); the substring search is the *data* view ("what did the model say about RAG?"). Both go straight to SQLite — same tables, different queries. Tomorrow you could add a `--retries-gt N` flag, an answer-length histogram, a per-run cost breakdown — any of them is one more function call to `con.execute(...)`. The persistence layer earns its keep.

**Watch for.**

- `OperationalError: no such table: answers` → you're pointing at a fresh `results.db`; run the pipeline first.
- Empty results → your pattern is too narrow. Use `""` (empty) to match everything.
- Numeric columns formatted as `nan` → `started_at` is None in one row; check the corresponding `write_run` call.

---

### Step 4d — Run end-to-end and verify · 💻 Self-paced · 10 min

**1. What we're doing & why.** Final sanity check before committing. Run the pipeline three times with different config (clean real, lossy real, clean fake), then query all three runs — confirming each got its own `run_id`, each has 20 answers, and the query script shows them cleanly.

**2. Where we are now.** Your pipeline runs end-to-end and persists one row to `runs` per execution. `results.db` has one row at the moment.

**3. What we're about to change.** Nothing in the code. We're just running the pipeline three times with different settings to populate the DB with three different shapes of run.

**4. Make the change — three runs in a row.**

Run 1 — real API, clean:

```bash
python -m src.pipeline.pipeline
```

Then edit `settings.py` to set `fail_rate=0.3` and run again:

```bash
python -m src.pipeline.pipeline                  # real, lossy
```

Then edit `settings.py` to set `use_fake=True` (and restore `fail_rate=0.0`) and run once more:

```bash
python -m src.pipeline.pipeline                  # fake, clean
```

**5. Run it — inspect what landed in the DB.**

```bash
python -m src.pipeline.query_results --runs
```

**6. What you should see.**

```
  id       started   questions   retries    cost_usd    fail  fake
   3       1718.2          20         0      0.0020    0.00     1           ← fake (use_fake=1)
   2       1718.0          20         5      0.0020    0.30     0           ← real, lossy (retries>0)
   1       1717.6          20         0      0.0020    0.00     0           ← real, clean
```

Verify each answer is tagged correctly:

```bash
sqlite3 results.db "SELECT run_id, COUNT(*) FROM answers GROUP BY run_id"
```

```
1|20
2|20
3|20             ← three runs, twenty answers each, all foreign-keyed correctly
```

**7. What just happened.** You can see the three runs distinctly: run 1 (real, clean, no retries), run 2 (real, lossy with retries — note the `5` in the retries column), run 3 (fake, clean — note `fake=1`). The summary fields differ as expected, and every one of the 60 answers is tagged with the right `run_id`. The pipeline is now a real piece of engineering: configurable, observable, persistent, queryable.

**Watch for.**

- One run has 0 answers → an exception interrupted the run before `write_answers` was called. Check `logs/pipeline.log` for the first `ERROR`.
- All answers share the same `run_id` → you forgot to capture `run_id` from `write_run`; using a stale value.

### ✅ Checkpoint 4

```bash
git add src/pipeline/store.py src/pipeline/query_results.py results.db
git commit -m "feat: SQLite persistence + runs table + query script"
git push
```

You should now have:

- Two tables — `runs` (one row per execution) and `answers` (each tagged with `run_id`).
- A query script that lists recent runs and searches answers by substring.
- Three or more runs persisted, all queryable.

---

## Step 5 — Coding-assistant mini-exercise (~20 min) · *do after Day 2*

The deliverable here is the **verification workflow you used**, not the feature itself.

### Step 5a — Pick a small improvement · 💻 Self-paced · 3 min

**1. What we're doing & why.** Pick a small feature to add to your pipeline using an AI coding assistant. The point is the habit, not the feature — so the smaller the better.

**2. Where we are now.** Your pipeline works. You're not modifying it for engineering reasons; you're modifying it to *practice* the assistant-verification habit.

**3. What we're about to do.** Choose one of these (or your own equivalent):

- Add a `--limit N` CLI flag that processes only the first N questions (useful during real-API debugging).
- Add total-cost reporting at the end (`sum(a.cost_usd for a in answers)` printed and logged).
- Add a `tqdm` progress bar around the batch loop (`pip install tqdm` first).
- Add a `--fail-rate` CLI flag that overrides `Settings`.
- Compute a real per-call cost from `resp.usage` instead of the placeholder `0.0001`.

**4. Make the change.** Pick one. Write it down on a piece of paper or in a draft `docs/lab2-assistant-notes.md` so it's locked in before you open the assistant.

**5. Run it.** Nothing to run yet.

**6. What you should see.** A chosen feature, scoped small enough to verify in 10 minutes.

**7. What just happened.** You've defined the scope before opening the assistant. This matters: opening an assistant with a vague intent is how scope creep happens.

---

### Step 5b — Use a coding assistant · 💻 Self-paced · 10 min

**1. What we're doing & why.** Use Cursor / Copilot / Claude Code / your tool of choice to implement the feature you picked — and do it with the five-step verification habit: **ask → read the diff → run the test → check for security → accept.**

> **If this fails live.** *Assistant unresponsive or unavailable? Type the change by hand and document what you* would *have asked. The deliverable is the verification workflow itself, not which tool drafted the lines.*

**2. Where we are now.** Pipeline works. Feature chosen but not implemented.

**3. What we're about to do.** Execute the five steps in order — they're the discipline:

1. **Ask** — a clear, single-purpose prompt for the feature.
2. **Read the diff** — every line is yours to defend.
3. **Run the test** — minimum: run the pipeline before and after the change.
4. **Check for security** — new dependency? change to how secrets are read? unsanitised input?
5. **Accept** — commit with a clear message.

**4. Make the change.** Open your assistant. Ask for the feature. *Read* what it produced — line by line. Run the pipeline.

**5. Run it.**

```bash
python -m src.pipeline.pipeline
```

**6. What you should see.**

```
wrote N answers to results.json in <time>s    ← N reflects your --limit if you added one;
                                                 nothing else should have regressed
```

**7. What just happened.** You used an assistant *with discipline*. Many learners feel pressure to accept whatever the assistant produced; the habit you're building is *to defend every line*. If the assistant introduced a dependency, you'll have seen it. If it changed unrelated lines, you'll have caught it. If it broke an existing test, you'll have noticed.

**Watch for.**

- Assistant adds a new dependency you didn't notice → `git diff requirements.txt` before committing.
- Assistant changes a line outside your scope → revert that line; small diffs are easier to review and defend.
- The change works for the fake path but breaks the real path (or vice versa) → run both, briefly, before committing.

---

### Step 5c — Document the workflow · 💻 Self-paced · 7 min

**1. What we're doing & why.** Write down what you just did. The note is the actual deliverable for this step. Documenting the verification habit makes it stick — and gives you a journal you'll thank yourself for in W22 when the assistant-suggested change is the one that breaks a multi-agent workflow.

**2. Where we are now.** Pipeline has your feature added. You haven't recorded what you asked, what came back, or what you verified.

**3. What we're about to do.** Create `docs/lab2-assistant-notes.md` with the template below, and *fill it in*.

**4. Make the change — create `docs/lab2-assistant-notes.md`:**

```markdown
# Lab 2 — Coding-assistant verification note

## The change
<one paragraph: what feature, why, what file(s)>

## The ask
<verbatim or paraphrased prompt you sent the assistant>

## What it produced
<short summary of the diff — what it added or changed>

## What I verified before accepting
- Diff read: <one line on what stood out>
- Test run: <what command you ran, what you saw>
- Security check: <new deps? secret-handling changes? unsanitised input?>

## What I changed before committing
<anything you tweaked — or "nothing"; both are fine answers>
```

Then **actually fill it in.** The empty template is not the deliverable.

**5. Run it.**

```bash
head -10 docs/lab2-assistant-notes.md
```

**6. What you should see.** The file exists, has your filled-in sections (not just the template), and is honest about what you did and didn't verify.

**7. What just happened.** You've turned an ephemeral assistant interaction into a durable record. In six months, when someone asks "how do we use AI assistants safely on this team?", you have a real example to show them.

**Watch for.**

- File is empty or has only the template → re-read your assistant log and fill it in honestly; this is the actual deliverable.

### ✅ Checkpoint 5

```bash
git add docs/lab2-assistant-notes.md src/pipeline/pipeline.py
git commit -m "feat: <your small improvement> + assistant verification note"
git push
```

---

## Submit

Paste your **repository URL** (or your W2 branch) into the cohort tracker. That's your Week 2 submission.

## Definition of done

- [ ] `src/pipeline/` package with `pipeline.py`, `fake_llm.py`, `logging_config.py`, `settings.py`, `store.py`, `query_results.py`.
- [ ] `data/questions.csv` with 20 rows; `logs/pipeline.log` with one JSON record per call.
- [ ] Pipeline runs end-to-end against the **real OpenAI API** for all 20 questions in batches of 5 with retries.
- [ ] **Two Pydantic models authored by you** — `Settings` (with `Field` constraints) and `RunSummary`. You can demonstrate one `ValidationError` firing on a bad input.
- [ ] `results.json` written with summary + answers; `results.db` populated with rows in both `runs` and `answers`; `query_results.py` returns matches for `--runs` and a substring search.
- [ ] `.env` is **not** tracked.
- [ ] `docs/lab2-assistant-notes.md` describes one improvement and the verification workflow.
- [ ] Repo URL submitted in the tracker.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'src'` | Run from the repo root with `python -m src.pipeline.pipeline`. |
| `ImportError: attempted relative import with no known parent package` | Same as above — use `python -m ...`. |
| `pydantic.ValidationError` when constructing `Settings` or `RunSummary` | A field violated a constraint (e.g. `batch_size=0`, `elapsed_seconds=-1`). The error names the field and the rule — read it. |
| `AuthenticationError` from OpenAI | On Vocareum the key is pre-set; open a fresh terminal. Off-Vocareum, check `.env` has `OPENAI_API_KEY=...` and `load_dotenv()` is being called. |
| `RateLimitError` on the real API run | Drop `Settings.batch_size` to 3 and try again. |
| `NotImplementedError: Step N — ...` | You're running the starter without filling in that step. Use the reference file. |
| `sqlite3.IntegrityError: NOT NULL constraint failed: answers.run_id` | You called `write_answers` before `write_run`, or didn't capture the returned `run_id`. |
| `results.json` is empty or missing the `summary` key | The script crashed before reaching the write — check `logs/pipeline.log` for the first `ERROR`; flip `use_fake=True` to isolate the bug from the API. |
| Pipeline takes ~30 s for 20 questions | You forgot `await` somewhere, so it's running serially. Compare timestamps in `logs/pipeline.log` — if they're seconds apart, that's the bug. |
| Logs not appearing in `logs/pipeline.log` | `get_logger()` wasn't called, or the `logs/` directory wasn't created. The `Path(log_path).parent.mkdir(...)` line handles it; verify it's there. |
| `pip install` fails on Vocareum | Add `--break-system-packages` or open a fresh Vocareum terminal. |
| Circular import between `pipeline.py` and `store.py` | Make sure `from .store import ...` is *inside* `if __name__ == "__main__":` in `pipeline.py`, not at the top. |

## Stretch goals (optional)

- Compute a real per-call cost from `resp.usage` (input / output tokens × the current `gpt-4o-mini` rate) instead of the placeholder `0.0001`. Update `RunSummary.total_cost_usd` accordingly.
- Add a `cli.py` module that builds `Settings` from `argparse`, so `python -m src.pipeline.cli --batch-size 3 --fail-rate 0.5 --use-fake` works end-to-end.
- Add a `replay.py` script that re-runs only the failed calls from the previous run (using the `runs` and `answers` tables).
- Replace the simple retry loop with `tenacity` decorators — and write a one-paragraph note on whether you prefer it.
- Add an `embed_question(q)` async function that fetches the embedding for each question alongside the answer and stores it as a JSON column. (This is the seed of next month's RAG work.)

## What's next

**Week 3 — LLM application foundations + model landscape.** The pre-read is in Slack. Bring questions from this week — the W3 session opens with anything you got stuck on here.
