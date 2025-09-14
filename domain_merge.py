
import csv
from pathlib import Path
from utils import infer_content_type, credibility_baseline

def load_lookup(path:str) -> dict:
    look = {}
    p = Path(path)
    if not p.exists():
        return look
    with p.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            d = (row.get("domain") or "").lower()
            if d:
                look[d] = {"type": row.get("type",""), "credibility": row.get("credibility","")}
    return look

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
            if d and label: flags[d] = label
    return flags

def merge_domain_metadata(input_csv:str, output_csv:str, lookup_csv:str, flagged_csv:str):
    lookup = load_lookup(lookup_csv)
    flagged = load_flagged(flagged_csv)
    inp = Path(input_csv); outp = Path(output_csv)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with inp.open(newline="", encoding="utf-8") as f, outp.open("w", newline="", encoding="utf-8") as g:
        r = csv.DictReader(f)
        fieldnames = list(r.fieldnames or [])
        if "domain_type" not in fieldnames: fieldnames.append("domain_type")
        if "credibility_score" not in fieldnames: fieldnames.append("credibility_score")
        if "flagged_label" not in fieldnames: fieldnames.append("flagged_label")
        w = csv.DictWriter(g, fieldnames=fieldnames); w.writeheader()
        for row in r:
            d = (row.get("domain") or "").lower()
            if d in lookup:
                tp = lookup[d].get("type") or ""
                cred = lookup[d].get("credibility") or ""
            else:
                tp = infer_content_type(d)
                cred = credibility_baseline(tp)
            row["domain_type"] = tp
            row["credibility_score"] = int(cred) if str(cred).isdigit() else cred
            row["flagged_label"] = flagged.get(d, "")
            w.writerow(row)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--lookup", required=True)
    ap.add_argument("--flagged", required=True)
    args = ap.parse_args()
    merge_domain_metadata(args.input, args.output, args.lookup, args.flagged)
