import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.eval.golden import load_golden_set, validate_golden_set
from src.eval.ragas_metrics import *
from src.eval.harness import *
from src.eval.judge import *

golden_path = Path(__file__).resolve().parent / "golden_set" / "capstone_v1.jsonl"

golden = load_golden_set(golden_path)
summary = validate_golden_set(golden_path)

rows = build_rows()
print('rows:', len(rows), '| kb_version:', active_kb_version())

sample = rows[0]
print('\n-- a healthy row --')
print('id:', sample['id'])
print('answer:', sample['answer'][:90], '...')
print('contexts:', len(sample['contexts']), 'chunks')

print('\n-- the seeded failures --')
for r in rows:
    if r['id'] in ('g005', 'g015', 'g019'):
        print(r['id'], '| contexts:', len(r['contexts']), '| note:', r['notes'][:40])
        
faith = score_faithfulness(rows)
print(faith)   # name=..., mode=offline-proxy, aggregate, n

print('\nlowest-scoring rows:')
for rid, sc in sorted(faith.per_row.items(), key=lambda kv: kv[1])[:5]:
    print(f'  {rid}: {sc:.3f}')    
    
results = score_all(rows)
for name, res in results.items():
    print(f'{name:20s} {res.aggregate:.3f}   ({res.mode})')    
    
good = JudgeScore(accuracy=4, groundedness=3, format=2, reasoning='correct, a bit terse')
bad  = JudgeScore(accuracy=2, groundedness=4, format=4, reasoning='beautifully wrong')
print('good  -> mean', round(good.mean, 2), '| task_success:', good.task_success)
print('bad   -> mean', round(bad.mean, 2),  '| task_success:', bad.task_success)