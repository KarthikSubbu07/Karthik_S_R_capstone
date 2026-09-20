# Lab 2 — Coding-assistant verification note

## The change
Adding an arg limit that is passed from CLI, this helps control the no of Q's I want to run, can be helpful when doing quick tests to check pipeline, such as smoke tests or sanity tests.

## The ask
I first asked co-pilot if it understood the current code, the structure and asked it to explain what I have built so far.  Then I asked its opinion about the feature using 
"""What is your suggestion to implement the below 
- Add a --limit N CLI flag that processes only the first N questions (useful during real-API debugging).""

## What it produced
Yes, I understand the code structure. Here's the overview:

**Project Purpose:**
A Week 2 capstone project demonstrating async LLM pipelines with retry logic and batch processing.

**Key Components:**

1. **Settings** - Pydantic config class with:
   - CSV path for input questions
   - Model name (gpt-4o-mini)
   - Batch size, fail rate, output paths
   - `use_fake` flag to toggle between real OpenAI vs fake LLM (for testing)

2. **Data Models** - `Question` (text input) and `Answer` (question, text, cost_usd, retries)

3. **Core Functions:**
   - `ask_llm()` - Single async LLM call (dispatches to fake or real)
   - `ask_llm_with_retry()` - Wraps it with exponential backoff (2^attempt seconds between retries)
   - `run_batch()` - Parallel gathering of single calls
   - `run_in_batches()` - Splits questions into chunks, processes each batch serially with 0.1s yield between them
   - `summarise_run()` - Aggregates stats (counts, total cost, retry metrics)

4. **Main Script** - Loads questions from CSV, runs the pipeline, writes results (summary + all answers) to JSON

**Current Status:**
- Works with fake LLM (no API needed)
- Real OpenAI path needs valid API key in `.env`
- Just fixed: CSV path resolution and `cost_usd` type (str→float)

Any specific part you want me to explain further?

## What I verified before accepting
- Diff read: The code changes in the pipeline file
- Test run: I implemented the changes and checked if it worked when passing 2 in the argument
- Security check: I had to add one import, argparser to parse arguments, i checked if it is safe to import before importing

## What I changed before committing
Updated the changes for the new feature