
import csv
from pathlib import Path
from utils import canonical_domain

def clean_serp(input_csv: str, output_csv: str, top_n:int=10):
    inp = Path(input_csv); outp = Path(output_csv)
    outp.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    with inp.open(newline="", encoding="utf-8") as f, outp.open("w", newline="", encoding="utf-8") as g:
        r = csv.DictReader(f)
        fieldnames = list(r.fieldnames or [])
        for col in ["keyword","engine","position","url"]:
            if col not in fieldnames: fieldnames.append(col)
        if "domain" not in fieldnames: fieldnames.append("domain")
        w = csv.DictWriter(g, fieldnames=fieldnames); w.writeheader()
        for row in r:
            try:
                pos = int(float(row.get("position", 9999)))
            except:
                pos = 9999
            if pos > top_n: continue
            url = (row.get("url") or "").strip()
            kw = (row.get("keyword") or "").strip()
            engine = row.get("engine","Google")
            key = (kw, engine, url)
            if key in seen: continue
            seen.add(key)
            row["domain"] = canonical_domain(url)
            w.writerow(row)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--top_n", type=int, default=10)
    args = ap.parse_args()
    clean_serp(args.input, args.output, args.top_n)
