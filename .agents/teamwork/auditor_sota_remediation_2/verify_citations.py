import re
import urllib.request
import json
import time

def extract_dois(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Match DOIs
    raw = re.findall(r'10\.\d{4,9}/[^\s\)\],;\"\'`]+', content)
    cleaned = set()
    for d in raw:
        d = d.rstrip('.').rstrip(']')
        cleaned.add(d)
    return cleaned

p1 = '/home/marques/Área de trabalho/2026.2/TCC/benchmarks/sota_assessment/sota_mapping_report.md'
p2 = '/home/marques/Área de trabalho/2026.2/TCC/benchmarks/sota_assessment/novelty_assessment_report.md'

d1 = extract_dois(p1)
d2 = extract_dois(p2)
all_dois = sorted(list(d1.union(d2)))

print(f"Total unique DOIs found: {len(all_dois)}")
for doi in all_dois:
    print(f"Checking: {doi}")
    url = f"https://api.crossref.org/works/{doi}"
    req = urllib.request.Request(url, headers={'User-Agent': 'mailto:auditor2@uesc.br'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))['message']
            title = data.get('title', ['<No Title>'])[0]
            authors = [a.get('family', '') for a in data.get('author', [])]
            container = data.get('container-title', [''])[0]
            print(f"  [OK] Title: {title[:70]}...")
            print(f"       Authors: {authors[:3]}")
            print(f"       Journal: {container}")
    except Exception as e:
        print(f"  [FAIL] Error fetching {doi}: {e}")
    time.sleep(0.2)
