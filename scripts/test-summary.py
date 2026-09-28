#!/usr/bin/env python3
import json
import sys
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else "e2e/results.json")
report = json.loads(path.read_text())
stats = report.get("stats", {})

failed = []


def collect(suite):
    for spec in suite.get("specs", []):
        if not spec.get("ok"):
            failed.append(f"{spec['title']} ({suite.get('title', '')})")
    for child in suite.get("suites", []):
        collect(child)


for suite in report.get("suites", []):
    collect(suite)

parts = [f"{stats.get('expected', 0)} passed"]
for count, label in (
    (stats.get("unexpected", 0), "failed"),
    (stats.get("flaky", 0), "flaky"),
    (stats.get("skipped", 0), "skipped"),
):
    if count:
        parts.append(f"{count} {label}")

print(f"{', '.join(parts)} in {stats.get('duration', 0) / 1000:.1f}s")
for title in failed:
    print(f"- `{title}`")
