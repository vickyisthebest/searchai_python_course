# lesson3_cleanserp.py
# Filters SERPs to top 10, classifies domain type, prints summaries, and saves outputs.

import os
import pandas as pd

INPUT_FILE = "serp_results.csv"
OUTPUT_TOP10 = "serp_results_top10.csv"
OUTPUT_DOMAIN_TYPE_COUNTS = "domain_type_counts.csv"
OUTPUT_DOMAIN_COUNTS = "domain_counts.csv"

# --- helpers ---------------------------------------------------------------

SOCIAL_DOMAINS = {
    "youtube.com", "youtu.be", "x.com", "twitter.com",
    "tiktok.com", "facebook.com", "instagram.com", "linkedin.com"
}

COMMUNITY_FORUMS = {  # treat separately from social media
    "reddit.com", "old.reddit.com", "quora.com"
}

NEWS_HINTS = {"news", "times", "guardian", "tribune", "post", "chronicle", "telegraph"}

# Optional: flag fossil-fuel/oil & gas domains as low-credibility for your audits
FOSSIL_FUEL_EXAMPLES = {
    # add client-specific domains here when you audit
    # e.g., "exxon.com", "shell.com", "bp.com"
}

def base_domain(host: str) -> str:
    if not isinstance(host, str) or not host:
        return ""
    host = host.strip().lower()
    # strip protocol and path if present
    for pref in ("http://", "https://"):
        if host.startswith(pref):
            host = host[len(pref):]
    host = host.split("/")[0]
    # drop www.
    if host.startswith("www."):
        host = host[4:]
    return host

def classify_domain(host: str) -> str:
    d = base_domain(host)

    if not d:
        return "unknown"

    # explicit lists first
    if d in COMMUNITY_FORUMS or any(d.endswith("." + f) for f in COMMUNITY_FORUMS):
        return "community_forum"

    if d in SOCIAL_DOMAINS or any(d.endswith("." + s) for s in SOCIAL_DOMAINS):
        return "social_media"

    if d in FOSSIL_FUEL_EXAMPLES:
        return "commercial_fossil_fuel"

    # tld-based signals
    if d.endswith(".gov") or ".gov." in d:
        return "government"
    if d.endswith(".edu") or d.endswith(".ac") or ".edu." in d or ".ac." in d:
        return "education"
    if d.endswith(".org") or ".org." in d:
        # orgs can be NGOs or just organizations; we keep it "ngo/org" for now
        return "ngo_org"

    # simple news heuristic (optional)
    if any(hint in d for hint in NEWS_HINTS):
        return "news_media"

    return "commercial"

# Simple credibility score (tweak later):
# higher = more authoritative
SCORES = {
    "government": 5,
    "education": 5,
    "ngo_org": 4,
    "news_media": 3,
    "community_forum": 2,   # Reddit/Quora (not social media)
    "social_media": 2,      # YouTube/Twitter/TikTok/etc.
    "commercial_fossil_fuel": 1,
    "commercial": 3,
    "unknown": 1,
}

# --- main ------------------------------------------------------------------

if not os.path.exists(INPUT_FILE):
    print(f"Error: The file '{INPUT_FILE}' was not found in this folder.")
    raise SystemExit(1)

try:
    df = pd.read_csv(INPUT_FILE)
except Exception as e:
    print(f"Error reading '{INPUT_FILE}': {e}")
    raise SystemExit(1)

if "Position" not in df.columns:
    print("Error: No 'Position' column found in your CSV.")
    raise SystemExit(1)

# Filter to top 10
df_top10 = df[df["Position"] <= 10].copy()

if df_top10.empty:
    print("No rows at Position ≤ 10. Nothing to summarize.")
    raise SystemExit(0)

# Normalize domain column if present; if not, try to infer from URL
if "Domain" in df_top10.columns:
    df_top10["Domain"] = df_top10["Domain"].astype(str).map(base_domain)
elif "URL" in df_top10.columns:
    df_top10["Domain"] = df_top10["URL"].astype(str).map(base_domain)
else:
    df_top10["Domain"] = ""

# Classify + score
df_top10["DomainType"] = df_top10["Domain"].map(classify_domain)
df_top10["CredibilityScore"] = df_top10["DomainType"].map(SCORES).fillna(1).astype(int)

# Save cleaned top10 file
df_top10.to_csv(OUTPUT_TOP10, index=False)

# Summaries
domain_counts = df_top10["Domain"].value_counts().rename_axis("Domain").reset_index(name="count")
domain_type_counts = df_top10["DomainType"].value_counts().rename_axis("DomainType").reset_index(name="count")

# Save summaries for your report pipeline
domain_counts.to_csv(OUTPUT_DOMAIN_COUNTS, index=False)
domain_type_counts.to_csv(OUTPUT_DOMAIN_TYPE_COUNTS, index=False)

# Print a concise console summary
print("Rows after filtering (≤10):", len(df_top10))
print(f"Saved cleaned dataset → {OUTPUT_TOP10}")
print("\nTop domains in filtered SERPs:")
print(domain_counts.head(10))

print("\nCounts by domain type:")
print(domain_type_counts)

# Special note for your reporting preference: highlight if social platforms appear
if (df_top10["DomainType"] == "social_media").any():
    print("\nNote: Social media results detected in top 10 — include a special note in the client summary.")
