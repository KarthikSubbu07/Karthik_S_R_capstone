"""Generate the Acme Analytics Platform corpus for W9 notebooks.

15 short docs designed to expose the tension between BM25 (exact-match keyword)
and dense semantic retrieval:
  - 5 feature descriptions (dense wins — synonym-heavy natural language)
  - 4 error code entries (BM25 wins — exact codes like AC-1042)
  - 3 pricing tier descriptions (mixed)
  - 3 API endpoint docs (BM25 wins — exact endpoint names like /v2/dashboards)

Reproducible — rerun this script to regenerate the corpus. Alternatively,
learners can add more entries by extending the CORPUS list below, or
substitute their own JSONL file with the same schema:
  {"id": str, "title": str, "text": str, "category": str}
"""
import json
from pathlib import Path

OUT = Path(__file__).parent / "sample_docs"
OUT.mkdir(exist_ok=True)

CORPUS = [
    # ─── Feature descriptions (dense wins — synonym-heavy) ───
    {
        "id": "feat_dashboards",
        "title": "Dashboards",
        "category": "feature",
        "text": (
            "Build interactive visualisations from your data warehouse without writing "
            "SQL. Drag-and-drop chart builder supports bar, line, area, scatter, and "
            "heatmap types. Dashboards can be embedded into external applications via "
            "signed iframes. Row-level security policies control which slices of data "
            "each user can see."
        ),
    },
    {
        "id": "feat_alerts",
        "title": "Alerting",
        "category": "feature",
        "text": (
            "Get notified when metrics cross thresholds you define. Alerts can trigger "
            "on absolute values, percentage changes, or anomaly detection over a rolling "
            "window. Notification channels include email, Slack, PagerDuty, and generic "
            "webhooks. Snooze alerts during planned maintenance windows."
        ),
    },
    {
        "id": "feat_scheduled_reports",
        "title": "Scheduled Reports",
        "category": "feature",
        "text": (
            "Automate delivery of dashboards as PDF, CSV, or Excel attachments to "
            "stakeholders. Schedules support daily, weekly, monthly, and custom cron "
            "cadences. Reports respect the recipient's row-level access — everyone "
            "gets the same layout with their own data."
        ),
    },
    {
        "id": "feat_data_explorer",
        "title": "Data Explorer",
        "category": "feature",
        "text": (
            "Ad-hoc data exploration for analysts who want SQL access. The explorer "
            "provides schema autocomplete, query history, and one-click chart preview "
            "for any query result. Query results can be saved as datasets that "
            "dashboards can then reference."
        ),
    },
    {
        "id": "feat_permissions",
        "title": "Access Control",
        "category": "feature",
        "text": (
            "Fine-grained permissions using roles, groups, and row-level security "
            "policies. Standard roles are Viewer, Editor, and Admin. Custom roles "
            "can be composed from primitive permissions. Row-level security uses "
            "SQL predicates evaluated per-user at query time."
        ),
    },
    # ─── Error code entries (BM25 wins — exact code lookup) ───
    {
        "id": "err_ac1042",
        "title": "AC-1042: Query timeout",
        "category": "error",
        "text": (
            "Error AC-1042 indicates a query exceeded the workspace timeout limit "
            "(default 60 seconds). Common causes: missing indexes on join columns, "
            "unbounded date ranges, or Cartesian joins. Resolution: add appropriate "
            "indexes in your data warehouse, or increase workspace timeout in "
            "Admin > Query Limits."
        ),
    },
    {
        "id": "err_ac2015",
        "title": "AC-2015: Insufficient permissions",
        "category": "error",
        "text": (
            "Error AC-2015 is raised when a user attempts an action their role does "
            "not permit. Check role assignments in Admin > Users. If the user should "
            "have access, verify the parent group has the permission enabled. "
            "Row-level security predicates can also produce this error when they "
            "evaluate to empty result sets."
        ),
    },
    {
        "id": "err_ac3301",
        "title": "AC-3301: Connector authentication failed",
        "category": "error",
        "text": (
            "Error AC-3301 indicates the data warehouse connector cannot authenticate. "
            "For Snowflake connections, verify the service account password has not "
            "expired. For BigQuery, check the service account JSON key is still valid "
            "and has the required roles. Recreate the connection under Settings > "
            "Data Sources if credentials have been rotated."
        ),
    },
    {
        "id": "err_ac4408",
        "title": "AC-4408: Dashboard render failure",
        "category": "error",
        "text": (
            "Error AC-4408 occurs when the dashboard rendering service cannot produce "
            "output for a scheduled report. Usually caused by a query in the "
            "dashboard timing out (see AC-1042), or by missing data for the "
            "recipient's row-level security scope. Check the dashboard runs "
            "interactively for the same user before debugging further."
        ),
    },
    # ─── Pricing tier descriptions (mixed) ───
    {
        "id": "price_starter",
        "title": "Starter Plan",
        "category": "pricing",
        "text": (
            "The Starter plan is $49 per user per month, billed annually. Includes up "
            "to 25 dashboards, 5 data source connections, and standard email support. "
            "Best for teams under 20 users piloting the platform."
        ),
    },
    {
        "id": "price_pro",
        "title": "Professional Plan",
        "category": "pricing",
        "text": (
            "The Professional plan is $99 per user per month, billed annually. Adds "
            "unlimited dashboards, unlimited connections, alerting, scheduled reports, "
            "and priority support. Recommended for teams of 20-200 users running "
            "day-to-day analytics."
        ),
    },
    {
        "id": "price_enterprise",
        "title": "Enterprise Plan",
        "category": "pricing",
        "text": (
            "The Enterprise plan supports unlimited seats with volume-based pricing "
            "starting at 200 users. Includes SSO/SAML, audit logging, custom retention "
            "policies, dedicated infrastructure, and a named customer success manager. "
            "Contact sales for a quote."
        ),
    },
    # ─── API endpoint docs (BM25 wins — exact endpoint match) ───
    {
        "id": "api_dashboards",
        "title": "POST /v2/dashboards",
        "category": "api",
        "text": (
            "Create a new dashboard. Request body accepts title (string, required), "
            "description (string, optional), layout (object, optional), and folder_id "
            "(string, optional). Returns the created dashboard object with a "
            "generated id. Requires the dashboards.write permission."
        ),
    },
    {
        "id": "api_query",
        "title": "POST /v2/query",
        "category": "api",
        "text": (
            "Execute an ad-hoc query against a connected data source. Request body "
            "requires source_id (string) and sql (string). Optional parameters: "
            "timeout_seconds (int, default 60), max_rows (int, default 10000). "
            "Returns a query result object with rows, columns, and row_count."
        ),
    },
    {
        "id": "api_alerts",
        "title": "GET /v2/alerts",
        "category": "api",
        "text": (
            "List all alerts visible to the authenticated user. Supports pagination "
            "via cursor (string) and limit (int, default 50, max 200). Response "
            "includes alert id, name, status (active/snoozed/triggered), and "
            "last_triggered_at timestamp. Requires the alerts.read permission."
        ),
    },
]


TEST_QUERIES = [
    {
        "q": "what's error code AC-1042 about",
        "expected_id": "err_ac1042",
        "expected_winner": "BM25",  # exact code — BM25 dominates
        "why": "exact error code AC-1042 — dense embeddings can miss alphanumeric IDs",
    },
    {
        "q": "how much does the enterprise plan cost",
        "expected_id": "price_enterprise",
        "expected_winner": "DENSE",  # synonym — "cost" not in doc, uses "pricing"/"quote"
        "why": "synonym gap — user says 'cost', doc says 'volume-based pricing' / 'quote'",
    },
    {
        "q": "POST /v2/dashboards endpoint parameters",
        "expected_id": "api_dashboards",
        "expected_winner": "BM25",  # exact endpoint path
        "why": "exact endpoint path — dense may generalise across all API docs",
    },
    {
        "q": "the queries in my report keep timing out",
        "expected_id": "err_ac1042",
        "expected_winner": "DENSE",  # semantic match to timeout
        "why": "conversational phrasing — user doesn't know the error code yet",
    },
    {
        "q": "how do I get notified when something breaks",
        "expected_id": "feat_alerts",
        "expected_winner": "DENSE",  # synonyms for alerting
        "why": "synonyms — 'notified when something breaks' == alerts on threshold crossing",
    },
    {
        "q": "GET /v2/alerts pagination cursor",
        "expected_id": "api_alerts",
        "expected_winner": "BM25",  # exact endpoint + parameter
        "why": "exact endpoint + parameter name — BM25 exact-match territory",
    },
]


def main():
    out_path = OUT / "acme_docs.jsonl"
    with out_path.open("w") as f:
        for doc in CORPUS:
            f.write(json.dumps(doc) + "\n")
    
    queries_path = OUT / "acme_test_queries.jsonl"
    with queries_path.open("w") as f:
        for q in TEST_QUERIES:
            f.write(json.dumps(q) + "\n")
    
    print(f"Generated {len(CORPUS)} docs → {out_path.name} ({out_path.stat().st_size} bytes)")
    print(f"Generated {len(TEST_QUERIES)} queries → {queries_path.name} ({queries_path.stat().st_size} bytes)")
    print()
    print("Corpus composition:")
    from collections import Counter
    cats = Counter(d["category"] for d in CORPUS)
    for cat, n in cats.items():
        print(f"  {cat:10s}  {n} docs")
    print()
    print("Want more variety?")
    print("  1. Extend the CORPUS list in this script — add more features, errors, endpoints")
    print("  2. Substitute your own JSONL file at sample_docs/acme_docs.jsonl with schema:")
    print("     {\"id\": str, \"title\": str, \"text\": str, \"category\": str}")


if __name__ == "__main__":
    main()
