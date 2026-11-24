"""Quick data quality inspector — not a test, run directly."""
import csv
from pathlib import Path

sources = [
    ('ml/data/processed/sift-pilot-v3-scam-fake-job/accepted.csv', 'SCAM'),
    ('ml/data/processed/sift-pilot-v2-legitimate-40/accepted.csv', 'LEGITIMATE'),
]
for path_str, label in sources:
    p = Path(path_str)
    with open(p, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    print(f'\n--- {label}: {len(rows)} rows ---')
    for r in rows:
        sid = r['sample_id']
        fam = r['template_family']
        msg = r['message_text'][:110]
        print(f'  [{sid}] fam={fam}')
        print(f'    {msg}')
