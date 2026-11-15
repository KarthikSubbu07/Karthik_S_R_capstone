"""scripts/init_results_db.py — add an eval-results table to results.db.

Reality check from the plan: at end of W10, `results.db` holds only the
semantic-cache tables (`query_cache`, `query_cache_meta`). The curriculum
says cost/latency come "from results.db", so W11 adds one small table that
logs per-query cost/latency/cache-hit for an eval run. test_kpi.py reads from
it when present (and falls back to the in-memory rows otherwise), so the
snapshot is reproducible without a live re-run.

Usage:
    python3 scripts/init_results_db.py            # create the table
    # then run_eval.py --persist writes rows into it
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = "./results.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS eval_results (
    run_label   TEXT    NOT NULL,
    kb_version  TEXT    NOT NULL,
    golden_id   TEXT    NOT NULL,
    cache_hit   INTEGER NOT NULL,
    latency_ms  INTEGER NOT NULL,
    cost_usd    REAL    NOT NULL,
    created_at  TEXT    DEFAULT (datetime('now')),
    PRIMARY KEY (run_label, golden_id)
);
"""


def init_db(db_path: str = DEFAULT_DB) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def write_rows(rows: list[dict], run_label: str, kb_version: str,
               db_path: str = DEFAULT_DB) -> int:
    """Persist per-query cost/latency for an eval run. Returns rows written."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.executemany(
            "INSERT OR REPLACE INTO eval_results "
            "(run_label, kb_version, golden_id, cache_hit, latency_ms, cost_usd) "
            "VALUES (?,?,?,?,?,?)",
            [(run_label, kb_version, r["id"], int(bool(r.get("cache_hit"))),
              int(r.get("latency_ms", 0)), float(r.get("cost_usd", 0.0)))
             for r in rows],
        )
        conn.commit()
        return len(rows)
    finally:
        conn.close()

# (The module's command-line entry point is intentionally omitted in the notebook.
#  Call init_db(...) and write_rows(...) directly instead, as the next cell does.)
