import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def fetch_serp(keyword: str, max_results: int = 100):
    if not SERPAPI_KEY:
        print("⚠️ No SERPAPI key found. Using dummy data instead.")
        return [{"keyword": keyword,
                 "position": i+1,
                 "title": f"Dummy result {i+1}",
                 "url": f"https://example.com/{i+1}",
                 "domain": "example.com",
                 "platform": "GoogleSERP"}
                for i in range(min(max_results, 10))]  # just 10 fake rows

    params = {
        "engine": "google",
        "q": keyword,
        "api_key": SERPAPI_KEY,
        "num": max_results
    }
    resp = requests.get("https://serpapi.com/search", params=params)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for rank, item in enumerate(data.get("organic_results", [])[:max_results], start=1):
        results.append({
            "keyword": keyword,
            "position": rank,
            "title": item.get("title"),
            "url": item.get("link"),
            "domain": item.get("displayed_link"),
            "platform": "GoogleSERP"
        })
    return results

if __name__ == "__main__":
    kw = "best solar panels"
    rows = fetch_serp(kw, max_results=20)
    for r in rows:
        print(r)
