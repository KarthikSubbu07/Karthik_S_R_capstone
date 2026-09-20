"""Persistence helpers for prompt evaluation results."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mp1_prompt_lab import JobDetails


RESULT_COLUMNS = (
    "strategy_name",
    "snippet_ID",
    "model_raw_response",
    "parsed_response",
    "cost_in_USD",
    "latency_in_seconds",
)


def init_results_db(db_path: str | Path = "data/results.db") -> None:
    """Create the evaluation results table if it does not exist."""
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS evaluation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                snippet_ID TEXT NOT NULL,
                model_raw_response TEXT NOT NULL,
                parsed_response TEXT NOT NULL,
                cost_in_USD REAL NOT NULL,
                latency_in_seconds REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(strategy_name, snippet_ID)
            )
            """
        )


def save_result(
    result: "JobDetails",
    db_path: str | Path = "data/results.db",
    csv_path: str | Path = "data/results.csv",
) -> None:
    """Persist one result to SQLite and upsert the CSV export."""
    db_path = Path(db_path)
    csv_path = Path(csv_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    init_results_db(db_path)

    values = tuple(result.model_dump()[column] for column in RESULT_COLUMNS)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO evaluation_results (
                strategy_name, snippet_ID, model_raw_response,
                parsed_response, cost_in_USD, latency_in_seconds
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(strategy_name, snippet_ID) DO UPDATE SET
                model_raw_response = excluded.model_raw_response,
                parsed_response = excluded.parsed_response,
                cost_in_USD = excluded.cost_in_USD,
                latency_in_seconds = excluded.latency_in_seconds
            """,
            values,
        )

    export_results_csv(db_path, csv_path)


def export_results_csv(
    db_path: str | Path = "data/results.db",
    csv_path: str | Path = "data/results.csv",
) -> None:
    """Export all SQLite results to a reproducible CSV snapshot."""
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            f"SELECT {', '.join(RESULT_COLUMNS)} FROM evaluation_results "
            "ORDER BY id"
        ).fetchall()

    with Path(csv_path).open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(dict(row) for row in rows)
