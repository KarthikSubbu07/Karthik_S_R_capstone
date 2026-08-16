# W1 — How to run and verify on Vocareum

This package contains exactly what a learner would have on disk after
finishing the W1 lab — no more, no less. Specifically:

```
W1_package/
├── src/
│   └── hello_llm.py           ← assembled from Lab Guide Steps 2b + 2c + 2d
├── docs/
│   ├── adr/                   ← empty; ADR is a markdown deliverable (Step 3)
│   └── runs/                  ← empty; Step 2e fills it with three .txt files
├── requirements.txt           ← matches Lab Guide Step 2a
└── RUN_W1.md                  ← this file
```

`hello_llm.py` was assembled by concatenating the three Python code
blocks the lab guide presents (Step 2b imports + dotenv, Step 2c the
`ask()` function, Step 2d the `__main__` block). Nothing was added,
removed, or rewritten.

---

## Step-by-step (each command is from the lab guide, verbatim)

### 1. Unzip and `cd` into the package

```bash
unzip AI-RAG_W1_Package.zip
cd W1_package
```

### 2. Verify Python + the OpenAI key are present *(Lab Guide §Before you start)*

```bash
python --version
```
Expected: `Python 3.11.x` (Vocareum's default is usually 3.10 or 3.11 — either is fine).

```bash
python -c "import os; print('OPENAI_API_KEY present:', bool(os.getenv('OPENAI_API_KEY')))"
```
Expected: `OPENAI_API_KEY present: True`

If `False`, open a fresh Vocareum terminal — the variable is set automatically there.

### 3. Install the two packages *(Lab Guide Step 2a)*

```bash
pip install --break-system-packages openai python-dotenv
```

Then sanity-check the install:

```bash
python -c "import openai, dotenv; print('OK ·', 'openai', openai.__version__)"
```
Expected: something like `OK · openai 1.50.0` (version number will vary).

### 4. Confirm the file parses + the client constructs *(Lab Guide Step 2b run-it)*

```bash
python -c "exec(open('src/hello_llm.py').read()); print('OK: client constructed')"
```
Expected: `OK: client constructed`

If you see `OpenAIError: The api_key client option must be set...`, the key isn't in your environment — go back to Step 2.

### 5. Make a real LLM call *(Lab Guide Step 2d run-it)*

```bash
python src/hello_llm.py "What is RAG in one sentence?"
```
Expected: a one-sentence answer about Retrieval-Augmented Generation. Anything sensible counts — model output isn't deterministic.

### 6. Save three runs to `docs/runs/` *(Lab Guide Step 2e — the lab's actual deliverable)*

```bash
python src/hello_llm.py "What is RAG in one sentence?"           > docs/runs/01-what-is-rag.txt
python src/hello_llm.py "Why might an LLM hallucinate?"          > docs/runs/02-why-hallucinate.txt
python src/hello_llm.py "Name three uses of vector databases."   > docs/runs/03-vector-db-uses.txt
```

Then confirm all three files were written and are non-empty:

```bash
ls -la docs/runs/
```
Expected: three files of a few hundred bytes each.

```bash
cat docs/runs/01-what-is-rag.txt
```
Expected: the same answer that printed in Step 5.

---

## What to send back to me

After running through, send me one of these so I can confirm W1 is good:

- The full terminal output from Steps 2-6, OR
- Just the result of `ls -la docs/runs/` + `cat docs/runs/01-what-is-rag.txt`, OR
- Any error you hit at any step.

If everything ran clean, I'll mark W1 as verified and compile W2 next.

## What I did NOT do

- Did not modify, simplify, or "fix" any code.
- Did not skip any steps from the lab guide.
- Did not auto-run anything for you — every command above is one *you* run on Vocareum so you see the actual behaviour.
