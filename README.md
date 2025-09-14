
# SearchAI MVP (Flagged Domains)

End-to-end pipeline for hybrid Traditional SERP + AI visibility audits with client-defined "flagged domains".

## Run with samples
```
python3 run_pipeline.py   --serp samples/serp_sample.csv   --ai samples/ai_sample.csv   --buckets samples/keywords_buckets_sample.csv   --client_domain bedsider.org   --outdir output
```

## Flagged domains (client-defined)
- Edit `data/flagged_domains.csv` with columns `domain,label`.
- Pipeline adds `flagged_label` wherever a domain matches.
- Alerts: `FLAGGED_IN_SERP`, `FLAGGED_IN_AI` include your label.

## SerpAPI ingestion (optional)
Install:
```
python3 -m pip install requests
```
Set key (macOS):
```
export SERPAPI_KEY="YOUR_KEY"
```
Run:
```
python3 serpapi_ingest.py --keywords samples/keywords_buckets_sample.csv --output output/serp_raw.csv
```
Then feed `output/serp_raw.csv` into the pipeline using `--serp output/serp_raw.csv`.
