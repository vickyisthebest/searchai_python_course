
import csv
from pathlib import Path
from utils import is_forum, is_social

def tag_forum_social(input_csv:str, output_csv:str):
    inp = Path(input_csv); outp = Path(output_csv)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with inp.open(newline="", encoding="utf-8") as f, outp.open("w", newline="", encoding="utf-8") as g:
        r = csv.DictReader(f)
        fieldnames = list(r.fieldnames or [])
        if "is_forum" not in fieldnames: fieldnames.append("is_forum")
        if "is_social" not in fieldnames: fieldnames.append("is_social")
        if "platform" not in fieldnames: fieldnames.append("platform")
        w = csv.DictWriter(g, fieldnames=fieldnames); w.writeheader()
        for row in r:
            d = (row.get("domain") or "").lower()
            forum = 1 if is_forum(d) else 0
            social = 1 if is_social(d) else 0
            platform = "Forum" if forum else ("Social" if social else "Web")
            row["is_forum"] = forum
            row["is_social"] = social
            row["platform"] = platform
            w.writerow(row)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    tag_forum_social(args.input, args.output)
