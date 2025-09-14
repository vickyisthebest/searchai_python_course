
from urllib.parse import urlparse

FORUM_DOMAINS = {"reddit.com", "old.reddit.com", "quora.com"}
SOCIAL_DOMAINS = {
    "youtube.com", "youtu.be", "twitter.com", "x.com", "tiktok.com",
    "instagram.com", "facebook.com", "fb.com", "linkedin.com"
}

def canonical_domain(url: str) -> str:
    if not url:
        return ""
    try:
        netloc = urlparse(url).netloc.lower()
        for prefix in ["www.", "m."]:
            if netloc.startswith(prefix):
                netloc = netloc[len(prefix):]
        return netloc
    except Exception:
        return ""

def is_forum(domain: str) -> bool:
    d = (domain or "").lower()
    return d in FORUM_DOMAINS or "reddit.com" in d or "quora.com" in d

def is_social(domain: str) -> bool:
    d = (domain or "").lower()
    return (d in SOCIAL_DOMAINS) or any(s in d for s in SOCIAL_DOMAINS)

def infer_content_type(domain: str) -> str:
    d = (domain or "").lower()
    if is_forum(d):
        return "Forum"
    if is_social(d):
        return "Social"
    if d.endswith(".gov"):
        return "Gov"
    if d.endswith(".edu") or d.endswith(".ac.uk") or ".edu." in d:
        return "Academic"
    if any(k in d for k in ["org", "ngo", "charity", "nonprofit"]):
        return "NGO"
    if any(k in d for k in ["news","press","times","guardian","cnn","bbc","reuters","apnews","nytimes"]):
        return "Media"
    return "Commercial"

def credibility_baseline(content_type: str) -> int:
    return {
        "Gov": 5, "Academic": 5, "NGO": 4, "Media": 3, "Commercial": 2, "Forum": 2, "Social": 2
    }.get(content_type, 2)
