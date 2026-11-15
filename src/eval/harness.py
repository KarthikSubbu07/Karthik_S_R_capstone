"""src/eval/harness.py — build the eval rows once, two ways.

Shared by eval/conftest.py (the pytest suite) and scripts/run_eval.py (the CLI),
so the offline synthetic pipeline and the live capstone pipeline are defined in
exactly one place.

Row shape (identical offline and live):
    {"id", "question", "answer", "contexts": [str,...], "ground_truth",
     "cache_hit", "latency_ms", "cost_usd", "notes"}
"""
from __future__ import annotations
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from eval.golden import load_golden_set
from eval.ragas_metrics import offline_mode

from pathlib import Path

# GoldenEntry, load_golden_set, offline_mode are defined in the cells above

REPO_ROOT = Path.cwd()   # notebook: resolve paths from the working directory
GOLDEN_PATH = REPO_ROOT / "golden_set" / "capstone_v1.jsonl"

# KB version active at eval time. Live mode reads it from the pipeline; offline
# pins the W10 value so every eval run and snapshot is tagged by KB state (D4).
OFFLINE_KB_VERSION = "v2.w10"

# A clean distractor sharing almost no content tokens with policy answers, so
# context precision reflects relevant-vs-retrieved honestly.
_DISTRACTOR = (
    "The office kitchen is restocked every Monday morning and the building "
    "reception desk is open from eight until six."
)


def _split_two(text: str) -> tuple[str, str]:
    words = text.split()
    mid = max(1, len(words) // 2)
    return " ".join(words[:mid]), " ".join(words[mid:])


def _synth_row(entry: GoldenEntry, index: int) -> dict:
    """Deterministically build one (answer, contexts) pair for a golden entry.

    Most rows are faithful and complete. A few are deliberately degraded so the
    report has real signal: g019 hallucinates, g015/g005 suffer retrieval misses.
    """
    gt = entry.ground_truth
    c1, c2 = _split_two(gt)
    contexts = [c1, c2, _DISTRACTOR]   # 2 relevant + 1 distractor
    answer = gt

    if entry.id == "g019":
        answer = gt + (" The company also matches up to five percent of salary "
                       "into a managed crypto retirement fund.")   # hallucination
    elif entry.id == "g015":
        contexts = [c1, _DISTRACTOR]                                # multi-hop miss
    elif entry.id == "g005":
        contexts = [c1[: max(1, len(c1) // 2)], _DISTRACTOR]        # weak retrieval

    cache_hit = index < 13          # ~65% warm hit rate, matching wk10
    return {
        "id":           entry.id,
        "question":     entry.question,
        "answer":       answer,
        "contexts":     contexts,
        "ground_truth": gt,
        "cache_hit":    cache_hit,
        "latency_ms":   184 if cache_hit else 785,
        "cost_usd":     0.000041 if cache_hit else 0.000412,
        "notes":        entry.notes,
    }


def _live_rows(golden: list[GoldenEntry]) -> list[dict]:  # pragma: no cover - live only
    """Run the real capstone over the golden set. Needs the learner's src/rag."""
    try:
        from src.rag.qdrant_rag import ask_rag
        from src.rag.qdrant_store import QdrantStore
        from src.rag.retrieval import (
            build_bm25_index,
            hybrid_retrieve,
            load_chunks_from_qdrant,
        )
    except Exception as exc:
        raise RuntimeError(
            "Live eval needs your capstone code (src/rag/*) on the path and "
            "OPENAI_API_KEY + QDRANT_URL set. Run offline with EVAL_OFFLINE=1. "
            f"Import error: {exc}"
        ) from exc

    store = QdrantStore()
    chunks = load_chunks_from_qdrant(store)          # tombstone-filtered (W10)
    bm25 = build_bm25_index(chunks)
    rows: list[dict] = []
    for e in golden:
        res = ask_rag(e.question, store, k=3)
        # Full chunk text for RAGAS contexts comes from retrieval, not from
        # ask_rag's stripped citations (D3).
        retrieved = hybrid_retrieve(store, bm25, chunks, e.question, top_k=3)
        rows.append({
            "id":           e.id,
            "question":     e.question,
            "answer":       res["answer"],
            "contexts":     [c.get("text", "") for c in retrieved],
            "ground_truth": e.ground_truth,
            "cache_hit":    res.get("cache_hit", False),
            "latency_ms":   res.get("latency_ms", 0),
            "cost_usd":     res.get("cost_usd", 0.0),
            "notes":        e.notes,
        })
    return rows


def active_kb_version() -> str:
    if offline_mode():
        return OFFLINE_KB_VERSION
    try:  # pragma: no cover - live only
        from src.rag.pipeline import KB_VERSION
        return KB_VERSION
    except Exception:  # pragma: no cover
        return "unknown"


def load_golden() -> list[GoldenEntry]:
    return load_golden_set(GOLDEN_PATH)


def build_rows(golden: list[GoldenEntry] | None = None) -> list[dict]:
    """The (question, answer, contexts, ground_truth, ...) rows under test."""
    golden = golden or load_golden()
    if offline_mode():
        return [_synth_row(e, i) for i, e in enumerate(golden)]
    return _live_rows(golden)
