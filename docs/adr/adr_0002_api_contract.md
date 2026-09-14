# ADR 0002 — /v1/ask API Contract

**Status:** Locked from Week 3.
**Defended at:** Design Review #1 (Week 5).
**Owners:** _Karthik SR_
**Date:** _2026-09-07_

## Context

By end of W3 the capstone has a FastAPI service. Every later week of this
programme will change something about the answer-generation core — different
models in W4, retrieval added in W6, reranking in W7+, agents in W19+. The
service's HTTP surface, however, needs to stay stable so that callers (the
Streamlit UI today, the evaluation harness in W5, eventually production
consumers) don't have to rewrite their integration each week.

This ADR locks the v1 API contract for /ask, /ask_batched, and /health.

## Decision

### Endpoint: `POST /ask`

**Request body (`Question`):**

| Field    | Type | Required | Notes                              |
|----------|------|:--------:|------------------------------------|
| question | str  |    Yes   | Free text. Min length 1.           |

**Response:** streamed `text/plain`. Tokens arrive as they are produced. The
complete response, if you concatenate every chunk, is the full answer.

### Endpoint: `POST /ask_batched`

Same input contract as `/ask`. Returns the full `Answer` body (JSON) without
streaming. Used for testing and for callers that can't consume streams.

**Response body (`Answer`):**

| Field        | Type  | Required | Notes                                       |
|--------------|-------|:--------:|---------------------------------------------|
| content      | str   |    Yes   | The generated answer.                       |
| cost_usd     | float |    Yes   | Cost of this call. Placeholder in W3; real in W4. |
| retries      | int   |    Yes   | Number of retries that fired in this call.  |

**Internal note:** The W2 pipeline that powers these endpoints uses different
field names internally (`text` instead of `question` and `content`). The
translation between the public contract and the internal model lives inside
each endpoint handler in `api/main.py`. This separation is intentional — the
internal model can change in W4+ without breaking the contract.

### Endpoint: `GET /health`

Returns `{"status": "ok"}` with HTTP 200 when the service is alive.

### Error responses

- `422 Unprocessable Entity` — request fails Pydantic validation. Body
  follows FastAPI's default `{detail: [...]}` shape.
- `5xx` — upstream LLM provider errors after retry budget exhausted. Body is
  a JSON `{detail: "..."}` with a short error message.

## Versioning Rule

- `/v1/ask` is locked from Week 3.
- **Don't bump** for additive changes:
  - New optional fields on Answer
  - Internal model swaps (including changes to the W2 pipeline's `text`-named fields)
  - Logging / observability changes
  - Retry-policy tweaks
  - Internal prompt edits
- **Do bump to /v2/ask** for breaking changes:
  - Field removal or rename on the *public* shape (Question, Answer)
  - Type change on a public field
  - Required ↔ optional change
  - Semantic change to a field's meaning
  - Change to the error-response shape
- When `/v2/ask` ships, `/v1/ask` runs in parallel for **at least 2 weeks**
  before retirement; consumers get an `X-Deprecation` warning header.
- Schema versioning on the response body lands in W4 (`schema_version` field
  added to `Answer`). The endpoint contract is separate from the body schema.

## Consequences

- **Positive.** The Streamlit UI, the W5 eval harness, and any later consumer
  integrate once. W4 → W30 internal changes happen behind the contract.
- **Negative.** We commit to maintaining `/v1/ask` even when its internals
  become legacy. Acceptable cost.
- **Open.** Authentication is out of scope for v1. When we layer it in W28/W29
  it will require an `Authorization` header but won't change the request or
  response shape itself.

## Tests securing this contract

- `tests/test_api.py::test_ask_rejects_missing_question` — validation contract.
- `tests/test_api.py::test_health_returns_ok` — /health contract.
- _(In W4)_ `tests/test_contract.py` — snapshot-test the `/openapi.json` to
  detect accidental contract breakage in CI.


### Cost budget (added W4)

Capstone `/ask_batched` calls cost ≤ **$0.0001 each** on average over a
representative batch of 10 questions. This is a soft budget — the
intent is to fail loud in observability if average cost suddenly
doubles, not to reject individual expensive calls.

The cohort confirms or refines this number against the actual results
of Lab Step 3 (`scripts/compare_models.py`).

### Chosen default model (added W4)

The default `Settings.model` is **`gpt-4o-mini`** for the lab. `gpt-4o`
is available via the same code path for harder questions or when the
mini model's confidence is low.

I would continue to proceed with gpt-40-mini because the cost doesnt justify the increase in quality.
So far based on the small dataset of 10 Q's we have compared and based on eyeballing the results, 40 doesnt justify the huge cost it bears compare dto mini.
Mini is still able to give reasonable and pretty much high/similar Quality responses and hence its good to stick with mini.