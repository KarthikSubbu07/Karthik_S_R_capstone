def _render_report(rows, kpis, extras, metrics) -> str:
    mode = extras["eval_mode"]
    banner = ""
    if mode == "offline-proxy":
        banner = (
            "> ⚠️ **MODE: offline-proxy.** These are deterministic token-overlap "
            "proxies for CI, **not** RAGAS numbers. Run live (`python3 "
            "scripts/run_eval.py`) for the numbers you put in the snapshot.\n\n"
        )
    lines = [
        "# wk11 RAGAS baseline (auto-generated)\n",
        banner,
        f"- **eval mode:** `{mode}`\n",
        f"- **kb_version:** `{extras['kb_version']}`\n",
        f"- **golden set:** {extras['n']} entries\n",
        "\n## RAG metrics (RAGAS)\n",
        "| Metric | Aggregate |\n|---|---|\n",
    ]
    for name in ("faithfulness", "answer_relevance",
                 "context_precision", "context_recall"):
        lines.append(f"| {name} | {metrics[name].aggregate:.3f} |\n")

    lines.append("\n## 8-KPI dashboard\n")
    lines.append("| # | KPI | Value |\n|---|---|---|\n")
    rowmap = [
        ("1", "Task success rate",     kpis["1_task_success_rate"]),
        ("2", "Grounded response rate", kpis["2_grounded_response_rate"]),
        ("3", "Hallucination rate",    kpis["3_hallucination_rate"]),
        ("4", "Retrieval hit rate",    kpis["4_retrieval_hit_rate"]),
        ("5", "Tool success rate",     kpis["5_tool_success_rate"]),
        ("6", "Cost per query (USD)",  kpis["6_cost_per_query_usd"]),
        ("7", "Latency p50 / p95 (ms)",
         f"{kpis['7_latency_p50_ms']:.0f} / {kpis['7_latency_p95_ms']:.0f}"),
        ("8", "Escalation rate",       kpis["8_escalation_rate"]),
    ]
    for num, label, val in rowmap:
        lines.append(f"| {num} | {label} | {val} |\n")

    lines.append("\n## W11 extensions (W10 tombstone payoff)\n")
    lines.append(
        f"- cache hit rate: {extras['cache_hit_rate']}\n"
        f"- cache-hit accuracy: {extras['cache_hit_accuracy']} · "
        f"cache-miss accuracy: {extras['cache_miss_accuracy']}\n"
        f"- results tagged `kb_version={extras['kb_version']}`\n"
    )

    lines.append("\n## Per-entry (lowest faithfulness first)\n")
    faith = metrics["faithfulness"].per_row
    lines.append("| id | faithfulness | notes |\n|---|---|---|\n")
    order = sorted(rows, key=lambda r: faith.get(r["id"], 0.0))
    for r in order[:6]:
        note = (r.get("notes", "") or "").split(".")[0][:48]
        lines.append(f"| {r['id']} | {faith[r['id']]:.3f} | {note} |\n")
    return "".join(lines)


# from IPython.display import Markdown, display
# metrics = out['metrics']
# report = _render_report(rows, kpis, extras, metrics)
# display(Markdown(report))