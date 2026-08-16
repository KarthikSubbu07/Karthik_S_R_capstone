# Week 1 — Hands-on Activity

**Title:** Reshape your assistant's voice — and feel how much leverage one line has.
**Time:** ~12–15 minutes
**Builds on:** the `hello_llm.py` you wrote during the live session.
**When to do this:** during the live session (immediately after the *What just happened?* slide, if there's time) — or as a 15-minute warm-up before starting the formal lab.

> The point of this activity isn't to write more code. It's to *see* that one line of system prompt is the single most leveraged change in your script — bigger than the model, bigger than the temperature, bigger than almost anything else you'll change all week.

---

## Goal

Run the same question four times, changing only the **system prompt** each time. Capture the four answers side-by-side. Write 2–3 sentences on what you notice.

## Materials

- `src/hello_llm.py` from class.
- A `docs/runs/week1-activity.md` file you'll create as you go.

---

## Steps

### 1. Run with the default prompt

In your terminal, run:

```bash
python src/hello_llm.py "Explain quantum entanglement in two sentences."
python /voc/work/hello_llm.py "Explain quantum entanglement in two sentences."
```



Copy the answer into `docs/runs/week1-activity.md` under a heading **Prompt A — "You are concise."**

### 2. Open `hello_llm.py` and find the system message

```python
{"role": "system", "content": "You are concise."},
```

### 3. Replace it with a kindergarten teacher

```python
{"role": "system", "content": "You are a kindergarten teacher. Explain like the listener is five years old."},
```

Run the same question. Save the answer under **Prompt B**.

### 4. Replace it with a Shakespearean poet

```python
{"role": "system", "content": "You are a Shakespearean poet. Reply in iambic verse where possible."},
```

Run again. Save the answer under **Prompt C**.

### 5. Replace it with a deliberately grumpy expert

```python
{"role": "system", "content": "You are a brilliant but impatient physicist. You explain accurately but you don't have time for niceties."},
```

Run again. Save the answer under **Prompt D**.

### 6. Reflect — 2 to 3 sentences in the same file

Under a heading **What changed?**, answer in your own words:

- What stayed the same across all four answers?
- What changed the most?
- Where would you reach for a *system prompt change* in a real product instead of fine-tuning the model?

---

## What you should notice

The *content* (quantum entanglement is a correlation between particles that persists even when separated, etc.) survives across all four answers — the physics doesn't change. What changes is **voice, vocabulary, sentence length, and tone**. A 30-character system-prompt edit moved the assistant from terse-academic to a kindergarten teacher without changing a model, a parameter, or a token of the user question.

That's why we tell teams: **before you propose fine-tuning, change the system prompt first.** Tens of dollars and one minute of work versus thousands of dollars and a week.

---

## Stretch (if you have ~5 extra minutes)

- Add `temperature=0.0` to your API call, run with Prompt A. Then `temperature=1.5`, run with Prompt A again. Compare — does it change *content* (what's said) or *style* (how it's said)?
- Try a **multi-turn** conversation by passing several `messages` (system, user, assistant, user) and see whether the assistant remembers the earlier exchange.
- Pick a question from your own capstone domain and run all four prompts on *that* — does the voice shift work as cleanly?

---

## Submit (optional but recommended)

Commit your `docs/runs/week1-activity.md` to your capstone repo:

```bash
git add docs/runs/week1-activity.md
git commit -m "feat: W1 activity — system-prompt voice exploration"
```

That file becomes a small artefact you can point at later when someone asks "why are system prompts a big deal?"
