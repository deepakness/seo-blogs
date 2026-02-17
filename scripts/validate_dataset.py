#!/usr/bin/env python3
import csv
import json
import re
import socket
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

CSV_PATH = Path('A List of 100+ SEO Blogs to Follow.csv')
JSON_PATH = Path('A List of 100+ SEO Blogs to Follow.json')
README_PATH = Path('README.md')


def fail(msg):
    raise SystemExit(f'VALIDATION FAILED: {msg}')


def main():
    csv_rows = list(csv.DictReader(CSV_PATH.open(encoding='utf-8-sig', newline='')))
    json_rows = json.loads(JSON_PATH.read_text(encoding='utf-8'))
    readme_text = README_PATH.read_text(encoding='utf-8')

    if not csv_rows:
        fail('CSV has no rows')

    # duplicate names not allowed
    name_counts = Counter(r['SEO Blog Name'] for r in csv_rows)
    dup_names = [n for n, c in name_counts.items() if c > 1]
    if dup_names:
        fail(f'duplicate blog names: {dup_names}')


    # duplicate URLs not allowed
    url_counts = Counter(r['SEO Blog URL'] for r in csv_rows)
    dup_urls = [u for u, c in url_counts.items() if c > 1]
    if dup_urls:
        fail(f'duplicate blog URLs: {dup_urls}')

    # validate JSON keys and parity
    for idx, row in enumerate(json_rows, start=1):
        if set(row.keys()) != {'blog_name', 'blog_url'}:
            fail(f'JSON row {idx} has unexpected keys: {sorted(row.keys())}')

    csv_pairs = [(r['SEO Blog Name'], r['SEO Blog URL']) for r in csv_rows]
    json_pairs = [(r['blog_name'], r['blog_url']) for r in json_rows]
    if csv_pairs != json_pairs:
        fail('CSV and JSON rows differ')

    # README parity
    readme_pairs = re.findall(r'^\d+\. \[(.*?)\]\((.*?)\)$', readme_text, flags=re.M)
    if csv_pairs != readme_pairs:
        fail('CSV and README list differ')

    if 'docs.google.com/spreadsheets' in readme_text:
        fail('README still contains Google Sheets link')

    # DNS resolution check for all hosts
    dns_errors = []
    for row in csv_rows:
        host = urlparse(row['SEO Blog URL']).hostname
        try:
            socket.getaddrinfo(host, None)
        except Exception as exc:
            dns_errors.append((row['SEO Blog Name'], row['SEO Blog URL'], str(exc)))

    if dns_errors:
        fail(f'DNS unresolved hosts found: {dns_errors[:3]}')

    print(f'Validation OK: {len(csv_rows)} entries, CSV/JSON/README in sync, DNS resolved.')


if __name__ == '__main__':
    main()
