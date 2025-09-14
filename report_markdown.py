import csv
from collections import defaultdict, Counter
from pathlib import Path

def load_buckets(path:str) -> dict:
    buckets = {}
    p = Path(path)
    if p.exists():
        with p.open(newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                kw = row.get("keyword","")
                b = row.get("bucket","General")
                if kw:
                    buckets[kw] = b
    return buckets

def gen_report(serp_csv:str, ai_csv:str, alerts_csv:str, bucket_csv:str, out_md:str, client_domain:str):
    buckets = load_buckets(bucket_csv)

    with open(serp_csv, newline="", encoding="utf-8") as f:
        serp_rows = list(csv.DictReader(f))
    with open(ai_csv, newline="", encoding="utf-8") as f:
        ai_rows = list(csv.DictReader(f))
    with open(alerts_csv, newline="", encoding="utf-8") as f:
        alerts = list(csv.DictReader(f))

    by_bucket_keywords = defaultdict(set)
    serp_vis = defaultdict(lambda: Counter())
    ai_vis   = defaultdict(lambda: Counter())
    flagged_counts = defaultdict(int)

    # SERP rows
    for row in serp_rows:
        kw = row.get("keyword","")
        b  = buckets.get(kw, "General")
        by_bucket_keywords[b].add(kw)
        platform = row.get("platform","Web")
        serp_vis[b][platform] += 1
        if (row.get("flagged_label") or ""):
            flagged_counts[b] += 1

    # AI rows
    for row in ai_rows:
        kw = row.get("keyword","")
        b  = buckets.get(kw, "General")
        ai_vis[b][row.get("platform","AI")] += 1

    # Alerts
    note_reddit  = defaultdict(bool)
    note_youtube = defaultdict(bool)
    for a in alerts:
        b = buckets.get(a.get("keyword",""), "General")
        if a["type"] in ("FORUM_IN_SERP","FORUM_IN_AI"):
            note_reddit[b] = True
        if a["type"] == "YOUTUBE_IN_AI":
            note_youtube[b] = True

    # Build report text
    lines = []
    lines.append("# Hybrid SEO + AI Audit Report\n")
    lines.append(f"Client domain: **{client_domain}**\n")

    for b in sorted(by_bucket_keywords.keys() or {"General"}):
        lines.append(f"## Bucket: {b}\n")
        lines.append(f"Keywords tracked: {len(by_bucket_keywords[b])}\n")

        sv = serp_vis[b]; av = ai_vis[b]
        lines.append("**SERP visibility by platform (count of top-10 results):** " +
                 ", ".join(f"{k}: {v}" for k, v in sv.items()) + "\n")
        lines.append("**AI visibility by platform (count of citations/mentions):** " +
                 ", ".join(f"{k}: {v}" for k, v in av.items()) + "\n")

        if flagged_counts[b] > 0:
            lines.append(f"**Flagged domains note:** {flagged_counts[b]} flagged results detected in top 10.\n")
        if note_reddit[b]:
            lines.append("**Special note:** Reddit/Quora surfaced for this bucket; ensure forum strategy is addressed.\n")
        if note_youtube[b]:
            lines.append("**Special note:** YouTube was cited by AI; consider a video asset for this bucket.\n")

        lines.append("**Actions:**\n")
        lines.append("- Urgent: Tackle keywords where flagged domains appear in top 10.\n")
        lines.append("- Short-term: Publish or optimize one high-E-E-A-T explainer for this bucket.\n")
        lines.append("- Long-term: Build forum and video assets if alerts indicate Reddit/YouTube presence.\n")
        lines.append("\n")

    Path(out_md).write_text("\n".join(lines), encoding="utf-8")
