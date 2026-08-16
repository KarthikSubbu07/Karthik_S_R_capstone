# Week 1 Lab — Frame Your Capstone & Make Your First LLM Call

**Programme:** Agentic AI & RAG Engineering
**Estimated time:** ~2 hours 15 min total · **Environment:** Vocareum (Python 3.11, OpenAI key pre-configured)
**Pacing:** Typically split across the two W1 days — Steps 1 + 2 after Day 1, Step 3 after Day 2. See *How to pace this* below.

---

## What we're building this week

In Day 1's live session you watched a real LLM call run and saw what your first script will produce. This lab is where you actually **build it**.

By the end of this lab, on your own machine you'll have:

- A **capstone repository** on GitHub (or local if push isn't ready yet), with a proper `.gitignore`, a `README.md`, and a clear `src/` + `docs/` layout.
- A working **`src/hello_llm.py`** that you wrote yourself — line by line, with the lab guide explaining the goal, the code, the run, and what the output means for every piece.
- **Three saved LLM runs** in `docs/runs/` that prove your script actually does what you said it does.
- A first **Architecture Decision Record** (`docs/adr/0001-capstone-framing.md`) that frames your capstone using the Solution Framing Canvas you'll see in Day 2.

The lab is intentionally hand-held this first week — every sub-step has the same shape, every code change is explained line by line, and every command shows you what the output should look like. By W3 you'll be moving faster; this week is about not getting lost.

## Learning outcomes

By finishing this lab you can:

1. Set up a clean Python project repository with secrets discipline in place.
2. **Author and run** a first OpenAI API call from Python, and explain each line.
3. Read an LLM response object and pull the answer text from it.
4. **Frame** a real problem as a Solution Framing Canvas (Inputs / Outputs / Tools / Memory / Autonomy level / Decision boundaries) and write it as an ADR.

---

## Before you start

You need:

- A Vocareum browser tab open (Python 3.11, OpenAI key pre-set).
- A GitHub account — useful but not required for W1 (you can keep the repo local this week).
- The deck from Day 1 nearby if you want to refer back to the architecture sketch or the four patterns.

Confirm your environment:

```bash
python --version       # expect Python 3.11.x
python -c "import os; print('OPENAI_API_KEY present:', bool(os.getenv('OPENAI_API_KEY')))"
# expect: OPENAI_API_KEY present: True
```

If the second command says `False`, open a fresh Vocareum terminal — the variable should be set automatically. If you're working off-Vocareum, you'll set up `.env` in Step 2b.

---

## How to pace this across the two W1 days

W1 is delivered over **Saturday + Sunday** (Day 1 + Day 2). The three lab steps map naturally onto the two evenings:

| When | Steps | Approx time | What you'll have done |
|------|-------|-------------|-----------------------|
| **Saturday evening** (after Day 1) | Step 1 — Create capstone repo · Step 2 — Build `hello_llm.py` | ~75 min | Repo committed · script working · 3 runs saved |
| **Sunday evening** (after Day 2) | Step 3 — Write ADR v1 (Solution Framing Canvas) | ~60 min | First ADR drafted in the repo |

If you can only do the lab in one sitting, all three steps work as a single ~2-hour-15-min chunk after Day 2. **The whole lab is due before Wednesday** so you're not racing into W2.

---

## How to read this guide

Every sub-step in this lab follows the same seven-beat shape, so you always know where you are:

1. **What we're doing & why** — the goal of this sub-step in plain language, before any code.
2. **Where we are now** — what your files / repo look like at the *start* of this sub-step.
3. **What we're about to change** — described in words first, so you know the plan.
4. **Make the change** — the exact code and commands, with line-by-line commentary where useful.
5. **Run it** — the literal command to execute.
6. **What you should see** — the literal expected output, with `←` arrows pointing at teaching moments.
7. **What just happened** — 2–4 sentences discussing what the output means and why it matters.

Plus, where useful:

- **Watch for** — two or three common ways this sub-step fails, and what each failure looks like.

Sub-step headers also carry a **mode tag** — `💻 Self-paced` — plus a time estimate. There's no "live demo" tag in this lab because every sub-step in W1 is self-paced.

---

## Step 1 — Create your capstone repository (~30 min) · *do after Day 1*

You set up the home your capstone will live in for the next 30 weeks. Three sub-steps: pick the corpus you'll work with, create the repo with secrets discipline, and add the project skeleton.

### Step 1a — Choose your corpus · 💻 Self-paced · 5 min

**1. What we're doing & why.** Your capstone needs a real, small body of documents to answer questions over. Picking it now (rather than later) keeps every later week grounded — by W7 we're chunking these documents, by W11 we're retrieving from them, by W22 they're behind your agent. Picking late means redoing W2's setup.

**2. Where we are now.** You don't have a corpus chosen yet. You may have an instinct from Day 1, but no commitment.

**3. What we're about to do.** Pick *one* corpus, in writing. The four options from Day 1's slide 14 are:

- **HR policies** (employee handbook, leave policy, benefits guide).
- **Product manuals** (a small set of technical product PDFs).
- **Public regulatory PDFs** (a SEBI / RBI / GDPR document set).
- **Open-source project documentation** (e.g. FastAPI, LangChain, NumPy docs).

Constraints (these matter — re-read slide 14 if needed):

- 5 to 20 documents — *not* hundreds.
- **No real PII or confidential data.** If you'd hesitate to let a peer review the corpus, swap it.
- Source must be reachable — if it's behind a login, swap it.

**4. Make the change.** Open a text file (any text editor or the Vocareum terminal) and write down — in one sentence — *the corpus you'll use and where you'll get it from*. Example:

```
My capstone corpus: FastAPI documentation (5 pages: tutorial intro, dependencies,
security, testing, deployment). Source: https://fastapi.tiangolo.com/
```

Don't download anything yet — that's a later week. Just commit the choice in writing.

**5. Run it.** No command to run. The act of writing the sentence is the run.

**6. What you should see.** A one-sentence commitment to your corpus on paper, in a notes app, or in a Vocareum text file. You'll paste this into your ADR in Step 3.

**7. What just happened.** You made the most important decision of W1 in five minutes. The corpus determines what's hard and what's easy in W7 (chunking), W11 (retrieval), W18 (eval), and W22 (the agent's tools). Locking the choice now means every later decision has a real anchor.

**Watch for.**

- *"I can't decide between two corpora."* → pick the one with **fewer documents** at first. You can grow the corpus later; you can't easily shrink an over-ambitious scope.
- *"My corpus is confidential."* → swap it. The cohort will see your repo for design reviews.

---

### Step 1b — Create the repository · 💻 Self-paced · 15 min

**1. What we're doing & why.** Stand up the directory + git layout your capstone will live in for 30 weeks. We do this *once* and carefully, so every later week has a clean home for new code, docs, runs, and ADRs.

**2. Where we are now.** No repository yet. Just a Vocareum terminal.

**3. What we're about to do.** Four moves:

1. Create a directory called `<your-name>-capstone` (or whatever short name you prefer).
2. Initialise git inside it.
3. Add a `.gitignore` that ignores secrets and cache files.
4. (Optional this week) Create a GitHub repo and push.

**4. Make the change.** In your Vocareum terminal, from your home directory:

```bash
mkdir <your-name>-capstone           # e.g. priya-capstone
cd <your-name>-capstone
git init
git branch -M main                   # use 'main' as the default branch
```

Then create `.gitignore` at the root with this content:

```
# Python
__pycache__/
*.pyc
.venv/
venv/

# Secrets — never commit these
.env
.env.local
*.key

# OS
.DS_Store
```

**Reading this `.gitignore`:**

- `__pycache__/` and `*.pyc` — Python's compiled bytecode cache; not meant for version control.
- `.venv/` / `venv/` — local virtual environments; each developer creates their own.
- `.env`, `.env.local`, `*.key` — **secrets**. The OpenAI API key lives in `.env` when you're off-Vocareum. **Never** in a tracked file.
- `.DS_Store` — macOS metadata files; irrelevant to your code.

**5. Run it — confirm git is happy.**

```bash
git status
```

**6. What you should see.**

```
On branch main                                                 ← branch is 'main' not 'master'
No commits yet
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        .gitignore                                             ← .gitignore is the only file so far

nothing added to commit but untracked files present
```

**7. What just happened.** You have an empty repository on the `main` branch with one file: `.gitignore`. The `.gitignore` is the single most important file in a new repo — it's the *promise* that your API keys won't end up on GitHub. Putting it in *first*, before anything else, is the right habit.

**(Optional)** Create the GitHub remote and push:

```bash
# After creating an empty repo at github.com/<your-username>/<your-name>-capstone:
git remote add origin git@github.com:<your-username>/<your-name>-capstone.git
git add .gitignore
git commit -m "chore: initialise repo with .gitignore"
git push -u origin main
```

If GitHub auth isn't set up on Vocareum yet, skip the push for now — we'll come back to it in W2 when push really matters. Your repo can live local-only this week.

**Watch for.**

- `git init` shows `master`, not `main` → run `git branch -M main` (older git versions default to `master`).
- The optional push step says `Permission denied (publickey)` → SSH key isn't on GitHub yet. Skip the push this week.

---

### Step 1c — Add the project skeleton · 💻 Self-paced · 10 min

**1. What we're doing & why.** Create the empty folders + files your capstone will need over the next 30 weeks. We don't fill them all today — but having the layout in place means every later week knows where its outputs go.

**2. Where we are now.** A `.gitignore` is the only file. No directories, no README.

**3. What we're about to do.** Create the layout:

- `src/` — Python code goes here.
- `docs/` — design documents (ADRs, Canvases) go here.
- `docs/adr/` — Architecture Decision Records.
- `docs/runs/` — saved LLM run outputs (we'll fill this in Step 2e).
- `README.md` — the front page of the repo.

**4. Make the change.** From the repo root:

```bash
mkdir -p src docs/adr docs/runs
touch src/.gitkeep docs/adr/.gitkeep docs/runs/.gitkeep
```

Then create `README.md` at the repo root with this content (replace `<Your Capstone Name>` and the corpus sentence):

```markdown
# Capstone — Knowledge Assistant

A 30-week build of a Q&A assistant over a small document corpus, completed as part of
the *Agentic AI & RAG Engineering* programme.

## Corpus

<one-sentence description from Step 1a — what corpus, source>

## Structure

- `src/` — application code
- `docs/adr/` — Architecture Decision Records (one per major design choice)
- `docs/runs/` — saved LLM outputs for evidence and reference

## Week 1

- [x] Set up repo + secrets discipline
- [ ] Build `hello_llm.py` (Lab Step 2)
- [ ] Write ADR v1 (Lab Step 3)
```

**Reading this `README.md`:**

- The corpus sentence is the same one you wrote in Step 1a. Pasting it here means anyone reading the repo knows the scope.
- `src/` and `docs/` separation is the conventional Python project layout — code in `src/`, design artefacts in `docs/`.
- `docs/adr/` is the standard location for [Architecture Decision Records](https://adr.github.io/) — a 6-line markdown file per major design choice, kept in version control.
- The Week 1 checklist at the bottom is your personal progress bar — tick boxes off as you complete the lab.
- The `.gitkeep` files inside the empty directories tell git "track this directory even though it's empty" (git doesn't track empty directories by default).

**5. Run it — confirm the layout.**

```bash
tree -L 2 -a -I '.git'
```

(If `tree` isn't installed, use `ls -la` and `ls -la src docs/adr docs/runs`.)

**6. What you should see.**

```
.
├── .gitignore                                                 ← from Step 1b
├── README.md                                                  ← just created
├── docs
│   ├── adr
│   │   └── .gitkeep                                           ← keeps the empty dir tracked
│   └── runs
│       └── .gitkeep
└── src
    └── .gitkeep
```

**7. What just happened.** Your capstone has its skeleton — six directories and files in place, exactly the shape it'll wear for the next 30 weeks. `src/` waits for Python code (Step 2 fills it); `docs/runs/` waits for the three LLM outputs (Step 2e fills it); `docs/adr/` waits for your first ADR (Step 3 fills it). The `README.md` documents the choice you made in Step 1a so it's not lost.

**Commit and (optionally) push:**

```bash
git add .gitignore README.md src docs
git commit -m "feat: project skeleton (src, docs/adr, docs/runs, README)"
git push                                                       # if remote is set up
```

### ✅ Checkpoint 1

You should now have:

- A repo named `<your-name>-capstone` on `main` branch.
- A `.gitignore` that excludes `.env`, `__pycache__`, etc.
- A `README.md` mentioning your corpus.
- Empty `src/`, `docs/adr/`, `docs/runs/` directories ready to fill.
- (Optional) A GitHub remote with the first commit pushed.

---

## Step 2 — Build `hello_llm.py` (~45 min) · *do after Day 1*

In this step you'll write your first real LLM call from scratch. Five sub-steps, each ~5–10 min. Take your time on **2c** in particular — that's where the actual API call lives.

### Step 2a — Install the packages · 💻 Self-paced · 5 min

**1. What we're doing & why.** Install the two Python packages we need. `openai` is the official OpenAI SDK. `python-dotenv` lets us load `OPENAI_API_KEY` from a `.env` file when you're off Vocareum (on Vocareum the key is already in the environment, so `dotenv` harmlessly no-ops).

**2. Where we are now.** Your repo has the skeleton from Step 1 but no Python packages installed yet. Running `python -c "import openai"` will fail with `ModuleNotFoundError`.

**3. What we're about to do.** Install both packages.

**4. Make the change.**

```bash
pip install openai python-dotenv
```

On Vocareum you may need to add `--break-system-packages`:

```bash
pip install --break-system-packages openai python-dotenv
```

**5. Run it — verify the install.**

```bash
python -c "import openai, dotenv; print('OK ·', 'openai', openai.__version__)"
```

**6. What you should see.**

```
OK · openai 1.x.x                                              ← v1 is what the SDK is on now
```

**7. What just happened.** Both packages imported cleanly. You're ready to write code. The version number is `1.x.x` — that's the major version of the OpenAI Python SDK that uses the `OpenAI()` client class (the older `openai.ChatCompletion.create(...)` style is v0; not what we want).

**Watch for.**

- `error: externally-managed-environment` → add `--break-system-packages` to the pip command.
- `openai 0.x.x` in the output → you have the old SDK. `pip install --upgrade openai`.

---

### Step 2b — Create `hello_llm.py` with imports + .env loading · 💻 Self-paced · 5 min

**1. What we're doing & why.** Start the file. We'll add the imports we need and the `load_dotenv()` call that reads `OPENAI_API_KEY` from a `.env` file if one exists. The key won't be in our code; we'll always pull it from the environment. That's the secrets discipline that runs through the rest of the programme.

**2. Where we are now.** `src/` exists but is empty (just a `.gitkeep`). No `hello_llm.py` yet.

**3. What we're about to do.** Create `src/hello_llm.py` with imports and environment loading. No actual API call yet — that lands in Step 2c.

**4. Make the change.** Create `src/hello_llm.py` with exactly this content:

```python
"""hello_llm.py — Your first OpenAI API call.

Run it from the repo root:
    python src/hello_llm.py "What is RAG in one sentence?"
"""
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load OPENAI_API_KEY from .env if a .env file exists.
# On Vocareum the key is already set in the environment, so this is a harmless no-op.
load_dotenv()

# Create the OpenAI client — it reads OPENAI_API_KEY from the environment automatically.
client = OpenAI()
```

**Reading this file line by line:**

- `"""hello_llm.py — ..."""` — a *module docstring*. The first thing in any Python file should describe what it does and show how to run it.
- `import sys` — standard library; we use `sys.argv` later in 2d to read command-line arguments.
- `from dotenv import load_dotenv` — lets us read `OPENAI_API_KEY` from a `.env` file. (We don't have a `.env` on Vocareum, but the function harmlessly does nothing if no file is found.)
- `from openai import OpenAI` — the official OpenAI Python SDK's main class.
- `load_dotenv()` — looks for a `.env` file in the current directory and any parent; reads any `KEY=value` lines and puts them in the environment. **Important security point:** the key never appears as a string literal in our code.
- `client = OpenAI()` — creates an OpenAI client. The SDK automatically reads `OPENAI_API_KEY` from the environment, so we don't pass it explicitly. This is intentional — passing the key as an argument would be the exact behaviour we're trying to avoid.

**5. Run it — confirm the file parses and the client constructs.**

```bash
python -c "exec(open('src/hello_llm.py').read()); print('OK: client constructed')"
```

**6. What you should see.**

```
OK: client constructed                                         ← imports + .env load + OpenAI() all worked
```

**7. What just happened.** The file exists, all three imports worked, `load_dotenv()` ran (silently — no `.env` to find on Vocareum), and `OpenAI()` constructed successfully (which means it found `OPENAI_API_KEY` in your environment). The client is ready to make a call — but we haven't told it what to ask yet. That's the next sub-step.

**Watch for.**

- `ModuleNotFoundError: No module named 'dotenv'` → Step 2a was skipped.
- `OpenAIError: The api_key client option must be set...` → `OPENAI_API_KEY` is missing from your environment. On Vocareum, open a fresh terminal. Off-Vocareum, create a `.env` file at the repo root with `OPENAI_API_KEY=sk-...` (note: `.gitignore` already ignores this file).

---

### Step 2c — Author the `ask()` function · 💻 Self-paced · 15 min

**1. What we're doing & why.** Define a function that takes a question (string), sends it to OpenAI, and returns the model's answer. This is the heart of the script — the place where the real API call happens.

**2. Where we are now.** `src/hello_llm.py` has imports, `load_dotenv()`, and `client = OpenAI()` — but no function and no API call.

**3. What we're about to do.** Append an `ask(question)` function to `src/hello_llm.py` that calls the chat completion endpoint and returns the answer text.

**4. Make the change.** Append this function to `src/hello_llm.py` (after the `client = OpenAI()` line):

```python


def ask(question: str) -> str:
    """Send one question to the LLM and return the answer text."""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are concise."},
            {"role": "user",   "content": question},
        ],
        temperature=0.3,
    )
    return resp.choices[0].message.content
```

**Reading this function line by line — this is the most important block in the file:**

- `def ask(question: str) -> str:` — defines a function called `ask` that takes one string argument and returns a string. The `: str` and `-> str` are *type hints* — they don't change the runtime behaviour, but they make the function's contract explicit.
- `"""Send one question to the LLM and return the answer text."""` — a *function docstring*. Always include one for functions you'd write a comment about.
- `client.chat.completions.create(...)` — the **chat completion** endpoint of the OpenAI API. This is the actual network call. Everything inside the parentheses is configuration for the call.
- `model="gpt-4o-mini"` — which OpenAI model to use. `gpt-4o-mini` is fast, cheap (~$0.15 per million input tokens), and good enough for almost all teaching use cases. We don't reach for the bigger models until we have a measured reason to.
- `messages=[...]` — the conversation. A list of role-content pairs. Two roles here:
  - `{"role": "system", "content": "You are concise."}` — the **system prompt**. Instructions to the model about how to behave (length, tone, persona). Always come first.
  - `{"role": "user", "content": question}` — the user message. This is the actual question, plugged in from the function's parameter.
- `temperature=0.3` — how random the response is. `0.0` ≈ always the same answer; `1.0+` ≈ varies a lot. `0.3` is mostly deterministic and good for factual answers.
- `resp.choices[0].message.content` — the response from the API is a structured object, not just a string. `choices[0]` picks the first (and, with default settings, only) candidate; `.message.content` is the text we want. The other fields on `resp` carry metadata (usage, token counts, finish reason) we'll use from W6 onward.

**5. Run it — call the function directly to confirm it works.**

```bash
python -c "
import sys; sys.path.insert(0, 'src')
from hello_llm import ask
print(ask('Say hello in one sentence.'))
"
```

**6. What you should see (something like).**

```
Hello! How can I assist you today?                             ← real model output, varies slightly per run
```

The exact words will vary (temperature isn't strictly zero), but it'll be a one-sentence hello.

**7. What just happened.** You made your first real LLM call. The script:

1. Imported the SDK and constructed the client (Step 2b's work).
2. Built a two-message conversation — a system prompt and your user question.
3. Sent it to `gpt-4o-mini` over HTTPS.
4. Got back a structured response.
5. Pulled out the text and printed it.

The whole round-trip cost a fraction of a cent. **You can defend every line of that function** — that's the W1 promise.

**Watch for.**

- `openai.AuthenticationError: Incorrect API key` → `OPENAI_API_KEY` isn't set. On Vocareum, open a fresh terminal.
- `openai.RateLimitError: ...` → rate limit on your account. Wait 30 seconds and try again, or check your account credits.
- The function returns `None` → you forgot the `return` statement. Re-read your file against the snippet above.

---

### Step 2d — Add `__main__` and run it from the command line · 💻 Self-paced · 10 min

**1. What we're doing & why.** Make the script runnable from the command line so you can pass a question as an argument. The `if __name__ == "__main__":` block is the standard Python idiom — code inside it runs when you execute the script directly, but *not* when you import it as a module (which is what we did in Step 2c).

**2. Where we are now.** `src/hello_llm.py` has imports + the client + the `ask()` function. Running `python src/hello_llm.py` does nothing visible because there's no entry-point block.

**3. What we're about to do.** Append a `__main__` block that reads the question from `sys.argv`, calls `ask()`, and prints the answer.

**4. Make the change.** Append to `src/hello_llm.py`:

```python


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "Say hello in one sentence."
    print(ask(q))
```

**Reading these three lines:**

- `if __name__ == "__main__":` — Python idiom. `__name__` is set to `"__main__"` when the script is run directly (`python src/hello_llm.py`), and set to the module name (`"hello_llm"`) when imported. The `if` guard means *"run this only when executed directly"* — exactly what we want for a command-line script.
- `q = " ".join(sys.argv[1:]) or "Say hello in one sentence."` — `sys.argv` is a list of command-line arguments. `sys.argv[0]` is the script name; `sys.argv[1:]` is everything after. `" ".join(...)` glues them into a single string (so multi-word questions don't need quotes). The `or "Say hello..."` provides a default if no argument was passed.
- `print(ask(q))` — call our function and print the answer.

**5. Run it — for real, from the command line, with a real question.**

```bash
python src/hello_llm.py "What is RAG in one sentence?"
```

**6. What you should see (something like).**

```
RAG, or Retrieval-Augmented Generation, is an approach that combines retrieval over a knowledge base with a generative language model to produce grounded, factual answers.
                                                               ← real answer; exact wording varies per run
```

**7. What just happened.** You ran your first LLM-backed command-line tool. The shell parsed your command, Python loaded the script, the `__main__` block joined `sys.argv[1:]` into the question string, the `ask()` function fired the API call, the response came back in ~1–3 seconds, and the answer printed. **Total cost:** about a hundredth of a cent. **Total lines you wrote:** about 20. This is the entire foundation that every later week extends.

**Watch for.**

- `python: can't open file '...src/hello_llm.py'` → you're not in the repo root. `cd` to the directory you created in Step 1b.
- The default "Say hello" answer prints even though you passed an argument → check you have spaces around the quotes and not curly quotes (some editors auto-replace `"` with `"` / `"`).

---

### Step 2e — Run three times with different questions and save the outputs · 💻 Self-paced · 10 min

**1. What we're doing & why.** Run the script three times with three different questions, and save each answer to a file in `docs/runs/`. These files are *evidence* — they prove your script actually does what you said it does. You'll reference them in Step 3 when writing the ADR.

**2. Where we are now.** `hello_llm.py` works. You've run it once with one question. `docs/runs/` is empty.

**3. What we're about to do.** Run the script three times, redirecting each output to a file in `docs/runs/`. Three distinct questions about your capstone domain, so the runs are *interesting* rather than identical hellos.

**4. Make the change.** Pick three questions related to your corpus (or use these defaults if you're not sure). For each one, redirect output with `>`:

```bash
python src/hello_llm.py "What is RAG in one sentence?" > docs/runs/01-what-is-rag.txt
python src/hello_llm.py "Why might an LLM hallucinate?" > docs/runs/02-why-hallucinate.txt
python src/hello_llm.py "Name three uses of vector databases." > docs/runs/03-vector-db-uses.txt
```

If your corpus is something other than the generic RAG examples, write questions that are more specific:

```bash
# Example for a FastAPI documentation corpus:
python src/hello_llm.py "What is dependency injection in FastAPI?" > docs/runs/01-di.txt
python src/hello_llm.py "Why use Pydantic models in API request validation?" > docs/runs/02-pydantic.txt
python src/hello_llm.py "How does FastAPI handle async endpoints?" > docs/runs/03-async.txt
```

**5. Run it — verify the files landed.**

```bash
ls -la docs/runs/
cat docs/runs/01-what-is-rag.txt
```

**6. What you should see.**

```
-rw-r--r--  1 you  staff  342 Jun  3 14:02 01-what-is-rag.txt        ← a few hundred bytes each
-rw-r--r--  1 you  staff  287 Jun  3 14:02 02-why-hallucinate.txt
-rw-r--r--  1 you  staff  401 Jun  3 14:02 03-vector-db-uses.txt
                                                                     ← then the file content:
RAG, or Retrieval-Augmented Generation, is an approach that combines retrieval
over a knowledge base with a generative language model to produce grounded,
factual answers.
```

**7. What just happened.** Three distinct LLM calls, three different answers, three saved files. These are now committed artefacts — they exist on disk, they'll go into git, and you'll reference them in Step 3 when describing what your capstone does. The discipline of *saving every meaningful run* will return in W6 when we start measuring LLM behaviour and in W22 when we trace agent runs. Start the habit now.

**Watch for.**

- A file is 0 bytes → the redirect happened *before* the script crashed. Check by running the command without `>` and see if you get an error.
- All three files contain identical text → check you actually changed the question between runs, and confirm `temperature=0.3` (not `0.0`).

### ✅ Checkpoint 2

```bash
git add src/hello_llm.py docs/runs/
git commit -m "feat: hello_llm.py + 3 saved runs"
git push                                                       # if remote is set up
```

You should now have:

- A working `src/hello_llm.py` that takes a question from the command line and prints an LLM answer.
- Three saved runs in `docs/runs/` — distinct questions, distinct answers, each a few hundred bytes.
- One git commit covering all four files.

---

## Step 3 — Write ADR v1: frame your capstone (~60 min) · *do after Day 2*

You write the first Architecture Decision Record for your capstone using the Solution Framing Canvas you saw in Day 2. The ADR is **the single most important artefact of W1** — it's the document a hiring manager could read in two minutes to understand what you've designed and why.

### Step 3a — Create `docs/adr/0001-capstone-framing.md` · 💻 Self-paced · 5 min

**1. What we're doing & why.** Create the empty ADR file with the right structure. The shape comes from the Solution Framing Canvas (Day 2, slide 38) — six boxes that capture *what the system is for, what it takes in, what it puts out, what tools it uses, what it remembers, and what it's allowed to decide for itself*. Filling these six boxes is your design.

**2. Where we are now.** `docs/adr/` exists but only has a `.gitkeep`. No ADR yet.

**3. What we're about to do.** Create `docs/adr/0001-capstone-framing.md` with the template structure. We'll fill it in 3b.

**4. Make the change.** Create `docs/adr/0001-capstone-framing.md` with this content:

```markdown
# ADR-0001: Capstone Framing — <Your Capstone Name>

- **Status:** Draft v1
- **Date:** <today's date in YYYY-MM-DD>
- **Author:** <your name>

## Context

<2–3 sentences: what problem is this capstone trying to solve, for whom, and why now?>

## Decision — Solution Framing Canvas

| Box | Your answer |
|-----|-------------|
| **Inputs** | <what the user / caller sends — text, file uploads, parameters> |
| **Outputs** | <what the system produces — a text answer, a citation list, a structured result> |
| **Tools** | <what external services it uses — OpenAI, your retriever, a database, …> |
| **Memory** | <what the system remembers between calls — nothing, last N turns, durable history> |
| **Autonomy level** | <on the spectrum from chatbot to agentic system, where this sits and why> |
| **Decision boundaries** | <what it's allowed to decide on its own, vs. what needs a human> |

## Consequences

- **Positive:** <2–3 bullet points: what this design unlocks>
- **Negative / risks:** <2–3 bullet points: what's harder / costlier / riskier because of this choice>
- **Things we'll re-visit:** <1–2 specific things we'll come back to in later ADRs>
```

**Reading this template:**

- **Status** — `Draft v1` for now. Later ADRs might be `Accepted`, `Superseded`, or `Deprecated`.
- **Six Canvas boxes** — these are the Solution Framing Canvas you saw on Day 2. Each box is *one* sentence; if you can't say it in one sentence, you don't understand the choice well enough yet.
- **Consequences** — positive, negative, things to revisit. Negative consequences matter as much as positive ones; we want learners to be honest about trade-offs from W1.

**5. Run it — confirm the file exists and parses as markdown.**

```bash
ls -la docs/adr/
head -5 docs/adr/0001-capstone-framing.md
```

**6. What you should see.**

```
0001-capstone-framing.md                                       ← exists
.gitkeep
                                                               ← then the file content:
# ADR-0001: Capstone Framing — <Your Capstone Name>

- **Status:** Draft v1
- **Date:** <today's date in YYYY-MM-DD>
```

**7. What just happened.** You've created the empty skeleton of your first ADR. The template forces you to answer six specific questions about your design before you start coding — which means you'll catch design holes *now*, not in W12 when refactoring is expensive. The file is empty of content but rich of structure — Step 3b fills it in.

---

### Step 3b — Fill it in for your corpus · 💻 Self-paced · 55 min

**1. What we're doing & why.** Replace every `<placeholder>` with your actual design decisions for your chosen corpus. This is the meaty part — expect 45–55 minutes of careful thinking, not typing. The quality of this ADR sets the bar for every later one.

**2. Where we are now.** The ADR file exists with the template structure. Every box is a `<placeholder>`.

**3. What we're about to do.** Fill in every section — Context, the six Canvas boxes, and Consequences — for *your* corpus. Below is an example for an HR-policies capstone to anchor what good answers look like. **Don't copy it verbatim** — adapt for your corpus.

**4. Make the change — fill in each section.**

**Title:** Replace `<Your Capstone Name>` with something specific, e.g. `Capstone Framing — HR Policy Assistant`.

**Status / Date / Author:** Fill them in. Use today's date in `YYYY-MM-DD` form.

**Context (2–3 sentences):** *Why does this need to exist? Who's the user?*

> *Example.* Our HR team fields ~40 routine policy questions per week — leave, benefits, expense limits — most of which are already documented in the employee handbook. A grounded Q&A assistant could deflect ~70% of these while keeping the human in the loop for the ambiguous 30%.

**The six Canvas boxes (one sentence each):**

- **Inputs.** What does the user send? *Example: a natural-language question (1–2 sentences), e.g. "How many sick days do I get in my first year?".*
- **Outputs.** What does the system return? *Example: a 2–4-sentence answer in plain English plus citation links pointing back to the source paragraph in the handbook.*
- **Tools.** What external services does it call? *Example: `gpt-4o-mini` for generation, a vector store (W7 will introduce) for retrieval over the chunked handbook.*
- **Memory.** What does it remember? *Example: nothing across sessions in v1 (every question is fresh); we'll revisit in W14 if multi-turn conversations land.*
- **Autonomy level.** Where on the spectrum? *Example: Q&A app — it answers, it doesn't act. No tool calls beyond retrieval. (Slide 9 of Day 1, between Chatbot and Workflow.)*
- **Decision boundaries.** What's it allowed to decide vs. escalate? *Example: it may answer any question whose retrieval confidence exceeds a threshold (TBD in W12); otherwise it returns "I'm not sure — please contact HR at hr@…".*

**Consequences:**

- **Positive (2–3 bullets):** what this design unlocks. *Example: deflects ~70% of routine traffic; gives an honest "I don't know" rather than guessing; citations build trust.*
- **Negative / risks (2–3 bullets):** what's harder / costlier / riskier. *Example: requires a maintained, up-to-date handbook; one bad citation could erode trust faster than ten good answers; no memory means context across questions is lost.*
- **Things we'll re-visit:** specific later-week revisits. *Example: confidence-threshold tuning in W12; multi-turn memory in W14; multilingual support in W19.*

**5. Run it — read your ADR aloud.**

```bash
cat docs/adr/0001-capstone-framing.md
```

Then read it out loud, slowly. If any sentence sounds wooly, the design isn't sharp enough — fix the sentence.

**6. What you should see.** A fully filled-in ADR with no `<placeholder>` text remaining. Every Canvas box is one specific sentence (not a hedge or a question). Every consequence is concrete.

```bash
grep -c '<' docs/adr/0001-capstone-framing.md     # should print 0 — no leftover placeholders
```

**7. What just happened.** You've turned a corpus idea into a defensible design in writing. The next time a peer asks *"what are you building?"*, you have a 2-minute answer. More importantly, every later week now has an anchor — when W7 makes you pick a chunking strategy, you can ask *"which strategy best supports my Inputs and Outputs from ADR-0001?"*. The decisions are no longer in your head; they're versioned in git.

**Commit and push:**

```bash
git add docs/adr/0001-capstone-framing.md
git commit -m "docs(adr): 0001 capstone framing — Solution Framing Canvas v1"
git push                                                       # if remote is set up
```

**Watch for.**

- *"My consequences box is empty."* → that means the design is too vague to have trade-offs. Be more specific in the Canvas boxes.
- *"I have five tools listed."* → for v1, you only have *one or two* (the LLM, optionally a retriever). The rest are W7+ decisions; don't pre-commit.
- *"My autonomy level changes depending on the day."* → pick the lowest level that still solves the problem. Autonomy adds risk; W1 isn't where you take on extra autonomy.

### ✅ Checkpoint 3

You should now have:

- A complete `docs/adr/0001-capstone-framing.md` with all six Canvas boxes filled in.
- No leftover `<placeholder>` text.
- One git commit referencing ADR-0001.

---

## Submit

Paste your **repository URL** (or your W1 branch) into the cohort tracker. That's your Week 1 submission. If your repo is local-only this week, paste a `git log --oneline` output instead — the cohort tracker accepts both.

## Definition of done

- [ ] A capstone repo named `<your-name>-capstone` on `main` branch.
- [ ] `.gitignore` excludes `.env`, `__pycache__`, `.venv`, `*.key`.
- [ ] `README.md` at the root, naming your corpus.
- [ ] `src/hello_llm.py` written by you, end-to-end runnable from the command line.
- [ ] **Three saved runs** in `docs/runs/` — distinct questions, distinct answers.
- [ ] `docs/adr/0001-capstone-framing.md` fully filled in (no `<placeholder>` text remaining).
- [ ] (Optional but encouraged) Repo pushed to GitHub.
- [ ] Repo URL submitted in the cohort tracker.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `python: command not found` | Use `python3` instead, or check Vocareum's terminal. |
| `ModuleNotFoundError: No module named 'openai'` | Step 2a was skipped — run `pip install openai python-dotenv` (add `--break-system-packages` on Vocareum if needed). |
| `openai.AuthenticationError: Incorrect API key` | `OPENAI_API_KEY` isn't set. On Vocareum, open a fresh terminal. Off-Vocareum, check your `.env` file. |
| `openai.RateLimitError` | Wait 30 seconds and try again, or check your account credits. |
| `openai 0.x.x` in `pip show openai` | You have the legacy SDK. `pip install --upgrade openai` to get v1+. |
| The script prints `None` | You forgot a `return` statement in `ask()`. Re-check Step 2c. |
| A saved run file is 0 bytes | The script crashed before any output was generated. Re-run without `>` to see the error. |
| `git init` shows `master`, not `main` | `git branch -M main` to rename. |
| GitHub push asks for password | SSH key not set up. Either set up an SSH key on GitHub, or skip the push this week and run the repo local-only. |
| ADR `grep -c '<'` shows 5+ | Placeholders left in the file. Use your editor's find to locate each `<…>` and fill it in. |

## Optional stretch goals

- Add a `--system` flag to `hello_llm.py` so you can override the system prompt from the command line.
- Add a third question to your three saved runs with a *deliberately ambiguous* phrasing, and observe whether the model hallucinates. Note the observation in your ADR's "Things we'll re-visit" section.
- Try the same three questions with `temperature=0.0` and `temperature=0.9`. Save them in `docs/runs/temperature-comparison/`. Write a one-paragraph note on which you'd ship to a user.
- Replace the `OpenAI()` import with the `AsyncOpenAI` client (W2 territory!) and rewrite `ask()` as `async def`. You'll need `asyncio.run(ask(...))` in `__main__`. This is a head-start on W2's content.

## What's next

**Week 2 — Async batch pipelines + Pydantic.** The pre-read is in Slack. You'll turn `hello_llm.py` into the seed of a 20-question async batch pipeline with typed config, retries, batching, and SQLite persistence. Bring questions from this week — Week 2 opens with anything you got stuck on here.
