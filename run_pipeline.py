
import argparse
from pathlib import Path
from serp_cleaner import clean_serp
from domain_merge import merge_domain_metadata
from forum_social_tracker import tag_forum_social
from ai_visibility_parser import parse_ai
from alerts import gen_alerts
from report_markdown import gen_report

def run_pipeline(serp_csv, ai_csv, buckets_csv, client_domain, outdir):
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    step1 = out / "serp_top10.csv"
    step2 = out / "serp_with_domains.csv"
    step3 = out / "serp_tagged.csv"
    ai_norm = out / "ai_normalized.csv"
    alerts_csv = out / "alerts.csv"
    report_md = out / "report.md"

    clean_serp(serp_csv, step1.as_posix(), top_n=10)
    merge_domain_metadata(step1.as_posix(), step2.as_posix(),
                          (Path(__file__).parent/"data/domain_lookup.csv").as_posix() if (Path(__file__).parent/"data/domain_lookup.csv").exists() else (Path(outdir)/"domain_lookup.csv").as_posix(),
                          (Path(__file__).parent/"data/flagged_domains.csv").as_posix())
    tag_forum_social(step2.as_posix(), step3.as_posix())
    parse_ai(ai_csv, ai_norm.as_posix())
    gen_alerts(step3.as_posix(), ai_norm.as_posix(), client_domain,
               (Path(__file__).parent/"data/flagged_domains.csv").as_posix(), alerts_csv.as_posix())
    gen_report(step3.as_posix(), ai_norm.as_posix(), alerts_csv.as_posix(), buckets_csv, report_md.as_posix(), client_domain)
    return report_md.as_posix()

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Run the SearchAI flagged-domain MVP pipeline")
    ap.add_argument("--serp", required=True)
    ap.add_argument("--ai", required=True)
    ap.add_argument("--buckets", required=True)
    ap.add_argument("--client_domain", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    report = run_pipeline(args.serp, args.ai, args.buckets, args.client_domain, args.outdir)
    print(f"Report written to {report}")
