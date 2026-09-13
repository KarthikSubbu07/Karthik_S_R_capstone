"""W4 STARTER — src/pipeline/models.py

This is the W3 shape with TODO markers for the additive W4 fields.
Lab Step 1c — extend Answer with confidence, sources, schema_version.

The W3 contract (content, cost_usd, retries) MUST be preserved — only add
optional fields with defaults so old clients keep working.
"""
from pydantic import BaseModel, Field


class Question(BaseModel):
    """Unchanged from W3."""
    question: str = Field(..., min_length=1)


class Answer(BaseModel):
    """W3 shape — extend with W4 fields below.

    Rule (from the ADR you'll update in Step 4): new fields must be optional
    with defaults. That keeps the W3 contract intact (additive change → no
    schema_version bump needed).
    """
    content: str
    cost_usd: float = 0.0001
    retries: int = 0
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    sources: list[str] = Field(default_factory=list)
    schema_version: str = "v1"