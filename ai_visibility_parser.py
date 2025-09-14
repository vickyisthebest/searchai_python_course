
import csv
from pathlib import Path
from utils import canonical_domain

def parse_ai(ai_csv:str, output_csv:str):
    inp = Path(ai_csv); outp = Path(output_csv)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with inp.open(newline="", encoding="utf-8") as f, outp.open("w", newline="", encoding="utf-8") as g:
        r = csv.DictReader(f)
        fieldnames = ["keyword","platform","cited_url","cited_domain","overview_present","date"]
        w = csv.DictWriter(g, fieldnames=fieldnames); w.writeheader()
        for row in r:
            url = (row.get("cited_url") or "").strip()
            w.writerow({
                "keyword": row.get("keyword",""),
                "platform": row.get("platform",""),
                "cited_url": url,
                "cited_domain": canonical_domain(url),
                "overview_present": row.get("overview_present","0"),
                "date": row.get("date","")
            })

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    parse_ai(args.input, args.output)
