# Lab 4 — Model comparison: gpt-4o-mini vs gpt-4o

**Cohort member:** _<your name>_
**Date:** _<dd/mm/yyyy>_

## Numbers (filled in by `scripts/compare_models.py`)

```
Model            n    Total $     Avg $/q     Time
---------------------------------------------------
gpt-4o-mini     10    0.000750    0.000075    18.98s
gpt-4o          10    0.014047    0.001405    26.83s

> gpt-4o cost 18.74 × more than gpt-4o-mini on the same questions.

## Two-paragraph eyeball reflection

### Paragraph 1 — where the gap mattered
Generic Q such as "Name two reasons to consider running a local model via Ollama.   " or  "How does streaming reduce perceived latency for an LLM app?  " the answers are pretty much the same from both models
But when the Q is more targetted such as "List two production timeouts every LLM app should set ", response from full is more structured and rounded, giving better information than mini

### Paragraph 2 — your rough rule for when to reach for the bigger model
If the application which we are developing needs more structure, accuracy and very high quality over quantity, and customer satisfaction is key, gpt-4o is the best recommended model.  Sure in terms of cost, mini beats 40 leaps and bounds, but 

## Confidence calibration (optional)

The lab pipeline asks the model to return a `confidence` value in `[0, 1]`.
Skim the persisted rows in SQLite:

```bash
sqlite3 data/answers.db \
  "SELECT model, AVG(confidence), AVG(cost_usd) FROM answers GROUP BY model;"
```

Do the two models report similar confidence on the same questions, or do
they disagree on what they know? One sentence is enough.
4o returns higher confidence scores compared to 4o-mini and thats probably not a surprise
but these answers and the correctness of these answers need to be evaluated to confirm the quakltiy of 4o.