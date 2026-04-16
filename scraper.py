#!/usr/bin/env python3
"""Scrapes Demonic Pacts League tasks from the OSRS wiki."""

import json
import re
import subprocess
import sys

URL = "https://oldschool.runescape.wiki/w/Demonic_Pacts_League/Tasks"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

TIER_ORDER = {"easy": 0, "medium": 1, "hard": 2, "elite": 3, "master": 4}


def fetch_html():
    result = subprocess.run(
        ["curl", "-s", "-L", "-A", UA, URL],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr}")
    return result.stdout


def strip_tags(html):
    text = re.sub(r"<[^>]+>", "", html)
    # decode basic HTML entities
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&#39;", "'").replace("&quot;", '"').replace("&nbsp;", " ")
    text = re.sub(r"&#\d+;", "", text)
    return text.strip()


def parse_tasks(html):
    tasks = []

    # Each task row looks like:
    # <tr id="3" data-taskid="3" data-league-area-for-filtering="general"
    #     data-league-tier="easy" data-league-points="10" data-pact-task="no">
    row_re = re.compile(
        r'<tr\s+id="(\d+)"\s+data-taskid="\d+"\s+'
        r'data-league-area-for-filtering="([^"]+)"\s+'
        r'data-league-tier="([^"]+)"\s+'
        r'data-league-points="(\d+)"[^>]*>(.*?)</tr>',
        re.DOTALL,
    )

    for m in row_re.finditer(html):
        task_id = int(m.group(1))
        region = m.group(2)
        tier = m.group(3)
        points = int(m.group(4))
        row_html = m.group(5)

        # Extract cells
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
        if len(cells) < 4:
            continue

        # col 0: area icon (skip)
        # col 1: name
        # col 2: description
        # col 3: requirements
        # col 4: points (with img)
        # col 5: comp%

        name = strip_tags(cells[1]) if len(cells) > 1 else ""
        description = strip_tags(cells[2]) if len(cells) > 2 else ""
        requirements = strip_tags(cells[3]) if len(cells) > 3 else ""
        comp_pct = strip_tags(cells[5]).rstrip("%") if len(cells) > 5 else ""

        if requirements in ("N/A", ""):
            requirements = ""

        tasks.append({
            "id": task_id,
            "name": name,
            "description": description,
            "region": region,
            "tier": tier,
            "tier_order": TIER_ORDER.get(tier, 99),
            "points": points,
            "requirements": requirements,
            "comp_pct": comp_pct,
        })

    # Sort by region, then tier, then name
    tasks.sort(key=lambda t: (t["region"], t["tier_order"], t["name"].lower()))
    return tasks


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "tasks.json"

    print(f"Fetching {URL} ...")
    html = fetch_html()
    print("Parsing tasks...")
    tasks = parse_tasks(html)
    print(f"Found {len(tasks)} tasks")

    with open(out, "w") as f:
        json.dump(tasks, f, indent=2)
    print(f"Saved to {out}")


if __name__ == "__main__":
    main()
