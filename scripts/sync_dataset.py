#!/usr/bin/env python3
import csv
import json
from pathlib import Path

CSV_PATH = Path('A List of 100+ SEO Blogs to Follow.csv')
JSON_PATH = Path('A List of 100+ SEO Blogs to Follow.json')
README_PATH = Path('README.md')


def pick_preferred(rows):
    """Keep one row per blog name, preferring HTTPS URLs."""
    chosen = {}
    order = []
    for row in rows:
        name = row['SEO Blog Name'].strip()
        url = row['SEO Blog URL'].strip()
        entry = {'SEO Blog Name': name, 'SEO Blog URL': url}
        if name not in chosen:
            chosen[name] = entry
            order.append(name)
            continue

        prev = chosen[name]['SEO Blog URL']
        if prev.startswith('http://') and url.startswith('https://'):
            chosen[name] = entry

    return [chosen[name] for name in order]


def rebuild_readme(rows):
    list_block = '\n'.join(
        f"{i}. [{r['SEO Blog Name']}]({r['SEO Blog URL']})"
        for i, r in enumerate(rows, start=1)
    )

    return f"""# 100+ SEO Blogs to Follow

A curated collection of SEO blogs for ongoing learning in search, technical SEO, local SEO, content strategy, and growth marketing.

## Dataset Files

- `A List of 100+ SEO Blogs to Follow.csv` — canonical source of truth.
- `A List of 100+ SEO Blogs to Follow.json` — machine-readable export with snake_case keys (`blog_name`, `blog_url`).

## Quick Stats

- Total blogs: **{len(rows)}**
- Validation: checked by `scripts/validate_dataset.py`

## SEO Blogs

{list_block}

## Validation Rules

- README list must exactly match CSV order and values.
- JSON export must exactly match CSV values.
- There must be no duplicate **blog names** or **blog URLs**.
- Removed or dead links should be pruned after verification.

## Contributing

1. Update the CSV file first.
2. Run `python scripts/sync_dataset.py`.
3. Run `python scripts/validate_dataset.py`.
4. Commit all resulting file changes together.
"""


def main():
    with CSV_PATH.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))

    rows = pick_preferred(rows)

    # Keep one row per URL (first occurrence order)
    seen_urls = set()
    deduped_rows = []
    for row in rows:
        if row['SEO Blog URL'] in seen_urls:
            continue
        seen_urls.add(row['SEO Blog URL'])
        deduped_rows.append(row)
    rows = deduped_rows

    with CSV_PATH.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['SEO Blog Name', 'SEO Blog URL'])
        writer.writeheader()
        writer.writerows(rows)

    json_rows = [{'blog_name': r['SEO Blog Name'], 'blog_url': r['SEO Blog URL']} for r in rows]
    JSON_PATH.write_text(json.dumps(json_rows, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    README_PATH.write_text(rebuild_readme(rows), encoding='utf-8')

    print(f'Synced dataset with {len(rows)} entries')


if __name__ == '__main__':
    main()
