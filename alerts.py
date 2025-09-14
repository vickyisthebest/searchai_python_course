
import csv
from pathlib import Path

FORUMS = {"reddit.com","old.reddit.com","quora.com"}
YOUTUBE = {"youtube.com","youtu.be"}

def load_flagged(path:str) -> dict:
    flags = {}
    p = Path(path)
    if not p.exists():
        return flags
    with p.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            d = (row.get("domain") or "").lower().strip()
            label = (row.get("label") or "").strip()
            if d and label:
                flags[d] = label
    return flags

def gen_alerts(serp_csv:str, ai_csv:str, client_domain:str, flagged_csv:str, output_csv:str):
    flagged = load_flagged(flagged_csv)
    inp_serp = Path(serp_csv); inp_ai = Path(ai_csv); outp = Path(output_csv)
    outp.parent.mkdir(parents=True, exist_ok=True)

    alerts = []
    with inp_serp.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            d = (row.get("domain") or "").lower()
            kw = row.get("keyword","")
            label = (row.get("flagged_label") or "").strip()
            if label:
                alerts.append({"keyword":kw, "type":"FLAGGED_IN_SERP", "detail": f"{d} ({label})"})
            if d in FORUMS:
                alerts.append({"keyword":kw, "type":"FORUM_IN_SERP", "detail": d})

    with inp_ai.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            d = (row.get("cited_domain") or "").lower()
            kw = row.get("keyword","")
            platform = row.get("platform","")
            if client_domain.lower() in d:
                alerts.append({"keyword":kw, "type":"AI_CITED_CLIENT", "detail": f"{platform}:{d}"})
            if d in FORUMS:
                alerts.append({"keyword":kw, "type":"FORUM_IN_AI", "detail": f"{platform}:{d}"})
            if d in YOUTUBE:
                alerts.append({"keyword":kw, "type":"YOUTUBE_IN_AI", "detail": f"{platform}:{d}"})
            if d in flagged:
                alerts.append({"keyword":kw, "type":"FLAGGED_IN_AI", "detail": f"{platform}:{d} ({flagged[d]})"})

    with outp.open("w", newline="", encoding="utf-8") as g:
        fieldnames = ["keyword","type","detail"]
        w = csv.DictWriter(g, fieldnames=fieldnames); w.writeheader()
        for a in alerts:
            w.writerow(a)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--serp", required=True)
    ap.add_argument("--ai", required=True)
    ap.add_argument("--client_domain", required=True)
    ap.add_argument("--flagged", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    gen_alerts(args.serp, args.ai, args.client_domain, args.flagged, args.output)
