
import csv
from collections import defaultdict, Counter
from pathlib import Path

def load_buckets(path:str) -> dict:
    buckets = {}
    p = Path(path)
    if not p.exists():
        return buckets
    with p.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            kw = row.get("keyword","")
            b = row.get("bucket","General")
            if kw: buckets[kw] = b
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
    ai_vis = defaultdict(lambda: Counter())
    flagged_counts = defaultdict(int)

    for row in serp_rows:
        kw = row.get("keyword","")
        b = buckets.get(kw, "General")
        by_bucket_keywords[b].add(kw)
        platform = row.get("platform","Web")
        serp_vis[b][platform] += 1
        if (row.get("flagged_label") or ""):
            flagged_counts[b] += 1

    for row in ai_rows:
        kw = row.get("keyword","")
        b = buckets.get(kw, "General")
        ai_vis[b][row.get("platform","AI")] += 1

    note_reddit = defaultdict(bool)
    note_youtube = defaultdict(bool)
    for a in alerts:
        b = buckets.get(a.get("keyword",""), "General")
        if a["type"] in ("FORUM_IN_SERP","FORUM_IN_AI"):
            note_reddit[b] = True
        if a["type"] == "YOUTUBE_IN_AI":
            note_youtube[b] = True

    lines = []
    lines.append(f"# Hybrid SEO + AI Audit Report
")
    lines.append(f"Client domain: **{client_domain}**
")

    for b in sorted(by_bucket_keywords.keys() or {"General"}):
        lines.append(f"## Bucket: {b}
")
        lines.append(f"Keywords tracked: {len(by_bucket_keywords[b])}
")
        sv = serp_vis[b]; av = ai_vis[b]
        lines.append("**SERP visibility by platform (count of top-10 results):** " + ", ".join(f"{k}: {v}" for k,v in sv.items()) + "
")
        lines.append("**AI visibility by platform (count of citations/mentions):** " + ", ".join(f"{k}: {v}" for k,v in av.items()) + "
")
        if flagged_counts[b] > 0:
            lines.append(f"**Flagged domains note:** {flagged_counts[b]} flagged results detected in top 10.
")
        if note_reddit[b]:
            lines.append(f"**Special note:** Reddit/Quora surfaced for this bucket; ensure forum strategy is addressed.
")
        if note_youtube[b]:
            lines.append(f"**Special note:** YouTube was cited by AI; consider a video asset for this bucket.
")
        lines.append("**Actions:**
")
        lines.append("- Urent: Tackle keywords where flagged domains appear in top 10.
")
        lines.append("- Short-term: Publish or optimize one high-E-E-A-T explainer for this bucket.
")
        lines.append("- Long-term: Build forum and video assets if alerts indicate Reddit/YouTube presence.
")
        lines.append("")
    Path(out_md).write_text("\n".join(lines), encoding="utf-8")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--serp", required=True)
    ap.add_argument("--ai", required=True)
    ap.add_argument("--alerts", required=True)
    ap.add_argument("--buckets", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--client_domain", required=True)
    args = ap.parse_args()
    gen_report(args.serp, args.ai, args.alerts, args.buckets, args.output, args.client_domain)
