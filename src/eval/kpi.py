"""src/eval/kpi.py — assemble the 8-KPI dashboard from scored rows.

This is the M2 deliverable's engine. It takes the scored eval rows and the
active kb_version and returns the full 8-KPI dashboard, plus the W11 extension
dimensions (cache-hit-rate and the cache-hit vs cache-miss accuracy split that
honours the W10 tombstone promise — D4).

The 8 KPIs (curriculum 'KPIs' sheet) and their W11 sources:
  1 Task success rate    — judge (live) / derived from grounded+relevant (offline)
  2 Grounded resp. rate  — RAGAS faithfulness
  3 Hallucination rate   — 1 - faithfulness (rough inverse)
  4 Retrieval hit rate   — RAGAS context precision
  5 Tool success rate    — N/A until W13 (no tools yet)
  6 Cost per query       — mean cost_usd (from results.db when present)
  7 Latency p50 / p95    — percentiles of latency_ms
  8 Escalation rate      — N/A until W17 (no HITL yet)
"""
from __future__ import annotations
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from eval.ragas_metrics import *

# score_all, offline_mode are defined in the cells above

TOOL_SUCCESS_NA = "N/A (W13 — no tools yet)"
ESCALATION_NA = "N/A (W17 — no HITL yet)"

# KPI #1 task-success bars when derived offline (no judge available).
# Grounded bar is set just above the hallucinated row's faithfulness so a
# hallucination counts as a task failure; the relevant bar catches off-topic.
_OFFLINE_GROUNDED_BAR = 0.65
_OFFLINE_RELEVANT_BAR = 0.40


def _percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile. p in 0..100."""
    if not values:
        return 0.0
    s = sorted(values)
    k = max(0, min(len(s) - 1, round((p / 100.0) * (len(s) - 1))))
    return float(s[k])


def _task_success_per_row(rows, metrics) -> dict[str, bool]:
    """Per-row task success. Live: the W5 judge. Offline: grounded AND relevant."""
    faith = metrics["faithfulness"].per_row
    rel = metrics["answer_relevance"].per_row

    if offline_mode():
        return {
            r["id"]: (faith.get(r["id"], 0) >= _OFFLINE_GROUNDED_BAR
                      and rel.get(r["id"], 0) >= _OFFLINE_RELEVANT_BAR)
            for r in rows
        }

    # Live: grade with the carried-forward W5 judge.
    from .judge import judge_one_sync  # pragma: no cover - live only
    out: dict[str, bool] = {}
    for r in rows:  # pragma: no cover - live only
        score = judge_one_sync(r["question"], r["answer"], r["ground_truth"])
        out[r["id"]] = score.task_success
    return out


def _rate(flags: dict[str, bool]) -> float:
    return round(sum(flags.values()) / len(flags), 4) if flags else 0.0


def compute_kpis(rows: list[dict], kb_version: str) -> dict:
    """Return {'kpis', 'extras', 'metrics'} for the snapshot and the KPI test."""
    metrics = score_all(rows)                       # 4 RAGAS metrics, one pass
    faith = metrics["faithfulness"]
    cprec = metrics["context_precision"]

    success = _task_success_per_row(rows, metrics)

    costs = [r["cost_usd"] for r in rows]
    lats = [float(r["latency_ms"]) for r in rows]
    hits = [r for r in rows if r.get("cache_hit")]
    misses = [r for r in rows if not r.get("cache_hit")]

    kpis = {
        "1_task_success_rate":     _rate(success),
        "2_grounded_response_rate": faith.aggregate,
        "3_hallucination_rate":    round(1.0 - faith.aggregate, 4),
        "4_retrieval_hit_rate":    cprec.aggregate,
        "5_tool_success_rate":     TOOL_SUCCESS_NA,
        "6_cost_per_query_usd":    round(sum(costs) / len(costs), 6) if costs else 0.0,
        "7_latency_p50_ms":        _percentile(lats, 50),
        "7_latency_p95_ms":        _percentile(lats, 95),
        "8_escalation_rate":       ESCALATION_NA,
    }

    # W11 extension dimensions — kb_version tag + cache split (D4).
    hit_success = {r["id"]: success[r["id"]] for r in hits}
    miss_success = {r["id"]: success[r["id"]] for r in misses}
    extras = {
        "kb_version":         kb_version,
        "eval_mode":          faith.mode,
        "cache_hit_rate":     round(len(hits) / len(rows), 4) if rows else 0.0,
        "cache_hit_accuracy": _rate(hit_success),
        "cache_miss_accuracy": _rate(miss_success),
        "n":                  len(rows),
    }
    return {"kpis": kpis, "extras": extras, "metrics": metrics}


def reportable_count(kpis: dict) -> tuple[int, int]:
    """(numeric KPIs, N/A KPIs). Distinct KPI rows 1-8 (latency counts once)."""
    na = sum(1 for k, v in kpis.items() if isinstance(v, str) and v.startswith("N/A"))
    # KPIs 1-8, but latency is split across two keys -> count distinct rows.
    distinct = {k.split("_", 1)[0] for k in kpis}
    return len(distinct) - na, na
