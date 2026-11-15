import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.eval.golden import load_golden_set, validate_golden_set
from src.eval.ragas_metrics import *
from src.eval.harness import *
from src.eval.judge import *
from src.eval.kpi import *
from src.eval.init_results_db import *
from run_eval import _render_report

golden_path = Path(__file__).resolve().parent / "golden_set" / "capstone_v1.jsonl"

golden = load_golden_set(golden_path)
summary = validate_golden_set(golden_path)

rows = build_rows()
kb_version = active_kb_version()
print('rows:', len(rows), '| kb_version:', kb_version)

# sample = rows[0]
# print('\n-- a healthy row --')
# print('id:', sample['id'])
# print('answer:', sample['answer'][:90], '...')
# print('contexts:', len(sample['contexts']), 'chunks')

# print('\n-- the seeded failures --')
# for r in rows:
#     if r['id'] in ('g005', 'g015', 'g019'):
#         print(r['id'], '| contexts:', len(r['contexts']), '| note:', r['notes'][:40])
        
# faith = score_faithfulness(rows)
# print(faith)   # name=..., mode=offline-proxy, aggregate, n

# print('\nlowest-scoring rows:')
# for rid, sc in sorted(faith.per_row.items(), key=lambda kv: kv[1])[:5]:
#     print(f'  {rid}: {sc:.3f}')    
    
# results = score_all(rows)
# for name, res in results.items():
#     print(f'{name:20s} {res.aggregate:.3f}   ({res.mode})')    
    
# good = JudgeScore(accuracy=4, groundedness=3, format=2, reasoning='correct, a bit terse')
# bad  = JudgeScore(accuracy=2, groundedness=4, format=4, reasoning='beautifully wrong')
# print('good  -> mean', round(good.mean, 2), '| task_success:', good.task_success)
# print('bad   -> mean', round(bad.mean, 2),  '| task_success:', bad.task_success)

out = compute_kpis(rows, kb_version)
kpis, extras = out['kpis'], out['extras']

print('=== 8-KPI dashboard ===')
for k, v in kpis.items():
    print(f'  {k:28s} {v}')

print('\n=== W11 extensions ===')
for k, v in extras.items():
    print(f'  {k:20s} {v}')

numeric, na = reportable_count(kpis)
print(f'\nreportable: {numeric} numeric + {na} N/A')


import sqlite3
init_db('results.db')
n = write_rows(rows, run_label='wk11-baseline', kb_version=kb_version, db_path='results.db')
print('persisted', n, 'rows')

conn = sqlite3.connect('results.db')
q = conn.execute('SELECT kb_version, COUNT(*), ROUND(AVG(cost_usd),6), ROUND(AVG(latency_ms),1) '
                 'FROM eval_results GROUP BY kb_version').fetchall()
conn.close()
print('kb_version | rows | avg cost | avg latency')
for row in q:
    print('  ', row)
    
    
from IPython.display import Markdown, display
metrics = out['metrics']
# report = _render_report(rows, kpis, extras, metrics)
# print(Markdown(report))
# baseline-set bars (see the deck / ADR): set just below the live baseline aggregate
THRESHOLDS = {'faithfulness': 0.85, 'answer_relevance': 0.85,
              'context_precision': 0.75, 'context_recall': 0.80}

print('metric              aggregate   bar     pass?')
for name, bar in THRESHOLDS.items():
    agg = metrics[name].aggregate
    print(f'  {name:18s} {agg:.3f}      {bar:.2f}    {agg >= bar}')

# (offline proxies won't all clear live-set bars — that's expected; the point is the
#  wiring. Run live, then set each bar just below the real aggregate.)