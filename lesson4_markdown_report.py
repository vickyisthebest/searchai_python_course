# lesson4_markdown_report.py
# Adds flagged_rows.csv (competitors/allies/taboos/scaremongering) and prints flag counts to terminal.

import os
import json
import pandas as pd
from datetime import datetime

INPUT_TOP10 = "serp_results_top10.csv"
CLIENT_PROFILE = "client_profile.json"
OUTPUT_MD = "serp_audit_summary.md"
OUTPUT_FLAGGED = "flagged_rows.csv"

SOCIAL_DOMAINS = {
    "youtube.com", "youtu.be", "x.com", "twitter.com",
    "tiktok.com", "facebook.com", "instagram.com", "linkedin.com"
}
COMMUNITY_FORUMS = {"reddit.com", "old.reddit.com", "quora.com"}
NEWS_HINTS = {"news", "times", "guardian", "tribune", "post", "chronicle", "telegraph"}

SCARE_TERMS = [
    "danger", "dangerous", "warning", "harmful", "ban", "illegal",
    "immoral", "scam", "toxic", "deadly", "avoid", "risk", "risks",
    "shocking", "exposed", "crisis", "threat"
]

def base_domain(host: str) -> str:
    if not isinstance(host, str) or not host:
        return ""
    h = host.strip().lower()
    if h.startswith("http://"): h = h[7:]
    elif h.startswith("https://"): h = h[8:]
    h = h.split("/")[0]
    if h.startswith("www."): h = h[4:]
    return h

def classify_domain(host: str) -> str:
    d = base_domain(host)
    if not d: return "unknown"
    # Always treat Reddit/Quora as community forums
    if d in COMMUNITY_FORUMS or any(d.endswith("." + f) for f in COMMUNITY_FORUMS):
        return "community_forum"
    if d in SOCIAL_DOMAINS or any(d.endswith("." + s) for s in SOCIAL_DOMAINS):
        return "social_media"
    if d.endswith(".gov") or ".gov." in d: return "government"
    if d.endswith(".edu") or d.endswith(".ac") or ".edu." in d or ".ac." in d: return "education"
    if d.endswith(".org") or ".org." in d: return "ngo_org"
    if any(hint in d for hint in NEWS_HINTS): return "news_media"
    return "commercial"

def has_scare_language(text: str) -> bool:
    if not isinstance(text, str): return False
    t = text.lower()
    return any(term in t for term in SCARE_TERMS)

# --- Load inputs
if not os.path.exists(INPUT_TOP10):
    print(f"Error: '{INPUT_TOP10}' not found. Run Lesson 3 first.")
    raise SystemExit(1)

if not os.path.exists(CLIENT_PROFILE):
    print(f"Error: '{CLIENT_PROFILE}' not found. Create it with competitors/allies/taboo.")
    raise SystemExit(1)

try:
    profile = json.load(open(CLIENT_PROFILE, "r"))
except Exception as e:
    print(f"Error reading {CLIENT_PROFILE}: {e}")
    raise SystemExit(1)

competitors = {base_domain(d) for d in profile.get("competitors", []) if d}
allies      = {base_domain(d) for d in profile.get("allies", []) if d}
taboo       = {base_domain(d) for d in profile.get("taboo", []) if d}
regions     = profile.get("regions", [])
languages   = profile.get("languages", [])

# --- Read SERP
try:
    df = pd.read_csv(INPUT_TOP10)
except Exception as e:
    print(f"Error reading {INPUT_TOP10}: {e}")
    raise SystemExit(1)

if "Domain" not in df.columns:
    if "URL" in df.columns:
        df["Domain"] = df["URL"].astype(str).map(base_domain)
    else:
        df["Domain"] = ""

df["Domain"] = df["Domain"].astype(str).map(base_domain)
df["DomainType"] = df["Domain"].map(classify_domain)

title_col = next((c for c in df.columns if c.lower() in {"title", "page title", "serp title"}), None)
desc_col  = next((c for c in df.columns if "description" in c.lower() or "snippet" in c.lower()), None)

df["IsCompetitor"] = df["Domain"].isin(competitors)
df["IsAlly"] = df["Domain"].isin(allies)
df["IsTaboo"] = df["Domain"].isin(taboo)
df["TitleScaremongering"] = df[title_col].apply(has_scare_language) if title_col else False
df["DescScaremongering"] = df[desc_col].apply(has_scare_language) if desc_col else False
df["AnyScaremongering"] = df["TitleScaremongering"] | df["DescScaremongering"]

# --- Aggregates
row_count = len(df)
dom_counts = df["Domain"].value_counts().rename_axis("Domain").reset_index(name="count")
dtype_counts = df["DomainType"].value_counts().rename_axis("DomainType").reset_index(name="count")
has_social = (df["DomainType"] == "social_media").any()
has_forum  = (df["DomainType"] == "community_forum").any()

competitor_hits = df[df["IsCompetitor"]]
ally_hits       = df[df["IsAlly"]]
taboo_hits      = df[df["IsTaboo"]]
scare_hits      = df[df["AnyScaremongering"]]

# --- Build Markdown
lines = []
lines.append("# SERP Audit Summary")
lines.append("")
lines.append(f"**Rows after filtering (≤10): {row_count}**")
lines.append("")
lines.append(f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_" )
lines.append("")

lines.append("## Top Domains")
for _, r in dom_counts.head(10).iterrows():
    lines.append(f"- {r['Domain']} ({r['count']})")
if len(dom_counts) == 0: lines.append("- None")
lines.append("")

lines.append("## Domain Types")
for _, r in dtype_counts.iterrows():
    lines.append(f"- {r['DomainType']}: {r['count']}")
if len(dtype_counts) == 0: lines.append("- None")
lines.append("")

lines.append("## Notes")
lines.append(f"- Community forums present: {'Yes' if has_forum else 'No'}")
lines.append(f"- Social media present: {'Yes' if has_social else 'No'}")
lines.append("")

lines.append("## Competitor Visibility")
if len(competitor_hits) == 0:
    lines.append("- None detected in top 10.")
else:
    for _, r in competitor_hits.iterrows():
        pos = r["Position"] if "Position" in r else "?"
        lines.append(f"- {r['Domain']} at position {pos}")
lines.append("")

lines.append("## Ally Presence")
if len(ally_hits) == 0:
    lines.append("- No allies detected in top 10.")
else:
    for _, r in ally_hits.iterrows():
        pos = r["Position"] if "Position" in r else "?"
        lines.append(f"- {r['Domain']} at position {pos}")
lines.append("")

lines.append("## Taboo Domains")
if len(taboo_hits) == 0:
    lines.append("- None detected in top 10.")
else:
    for _, r in taboo_hits.iterrows():
        pos = r["Position"] if "Position" in r else "?"
        lines.append(f"- {r['Domain']} at position {pos} — review advised")
lines.append("")

lines.append("## Potential Scaremongering / Stigma Language")
if len(scare_hits) == 0:
    lines.append("- None detected in titles/descriptions.")
else:
    show_cols = ["Position", "Domain"]
    if title_col: show_cols.append(title_col)
    if desc_col:  show_cols.append(desc_col)
    for _, r in scare_hits[show_cols].head(10).iterrows():
        pos = r.get("Position", "?")
        dom = r.get("Domain", "")
        title_txt = r.get(title_col, "").strip() if title_col else ""
        lines.append(f"- {dom} at position {pos}: {title_txt[:140]}{'...' if len(title_txt) > 140 else ''}")
lines.append("")

with open(OUTPUT_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"Wrote Markdown summary → {OUTPUT_MD}")

# --- Flagged rows CSV (competitor/ally/taboo/scaremongering only)
flag_mask = df["IsCompetitor"] | df["IsAlly"] | df["IsTaboo"] | df["AnyScaremongering"]
flagged = df[flag_mask].copy()

# Choose compact, useful columns if present
keep_cols = []
for c in ["Keyword", "Position", "Domain", "URL", "DomainType", "IsCompetitor", "IsAlly", "IsTaboo",
          "TitleScaremongering", "DescScaremongering", "AnyScaremongering"]:
    if c in flagged.columns:
        keep_cols.append(c)
if title_col and title_col not in keep_cols: keep_cols.append(title_col)
if desc_col and desc_col not in keep_cols: keep_cols.append(desc_col)

if flagged.empty:
    pd.DataFrame(columns=keep_cols if keep_cols else ["Domain"]).to_csv(OUTPUT_FLAGGED, index=False)
    print(f"No flagged rows. Wrote empty template → {OUTPUT_FLAGGED}")
else:
    flagged = flagged[keep_cols] if keep_cols else flagged
    flagged.sort_values(by=[c for c in ["Keyword", "Position"] if c in flagged.columns], inplace=True)
    flagged.to_csv(OUTPUT_FLAGGED, index=False)
    print(f"Wrote flagged rows → {OUTPUT_FLAGGED} (rows: {len(flagged)})")

# --- Terminal summary (new)
print("\nSummary:")
print(f"- Competitor hits: {len(competitor_hits)}")
print(f"- Ally hits:       {len(ally_hits)}")
print(f"- Taboo hits:      {len(taboo_hits)}")
print(f"- Scaremongering:  {len(scare_hits)}")
