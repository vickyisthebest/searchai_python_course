
import os, csv, time, argparse, requests
from pathlib import Path

API_URL = "https://serpapi.com/search.json"

def fetch_top_results(keyword:str, api_key:str, engine:str="google", country:str="us", language:str="en", num:int=10):
    params = {"engine": engine, "q": keyword, "num": num, "api_key": api_key, "gl": country.lower(), "hl": language.lower()}
    r = requests.get(API_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    results = []
    org = data.get("organic_results") or []
    for item in org:
        pos = item.get("position"); link = item.get("link") or item.get("url")
        if pos and link:
            results.append({"position": int(pos), "url": link})
        if len(results) >= num: break
    return results

def main():
    ap = argparse.ArgumentParser(description="Fetch top results via SerpAPI and write CSV for the pipeline")
    ap.add_argument("--keywords", required=True)
    ap.add_argument("--engine", default="google")
    ap.add_argument("--country", default="us")
    ap.add_argument("--language", default="en")
    ap.add_argument("--num", type=int, default=10)
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--output", default="serp_raw.csv")
    args = ap.parse_args()

    api_key = os.getenv("SERPAPI_KEY")
    if not api_key: raise RuntimeError("Missing SERPAPI_KEY environment variable.")

    inp = Path(args.keywords); outp = Path(args.output); outp.parent.mkdir(parents=True, exist_ok=True)
    kws = []
    with inp.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        if "keyword" not in r.fieldnames: raise ValueError("Keywords CSV must have a 'keyword' column")
        for row in r:
            kw = (row.get("keyword") or "").strip()
            if kw: kws.append(kw)
    with outp.open("w", newline="", encoding="utf-8") as g:
        fieldnames = ["keyword","engine","position","url"]
        w = csv.DictWriter(g, fieldnames=fieldnames); w.writeheader()
        for kw in kws:
            try:
                results = fetch_top_results(kw, api_key, engine=args.engine, country=args.country, language=args.language, num=args.num)
                for row in results:
                    w.writerow({"keyword": kw, "engine": args.engine.capitalize(), "position": row["position"], "url": row["url"]})
            except Exception as e:
                w.writerow({"keyword": kw, "engine": args.engine.capitalize(), "position": "", "url": f"ERROR: {e}"})
            time.sleep(args.delay)
    print(f"Wrote {outp.as_posix()}")

if __name__ == "__main__":
    main()
