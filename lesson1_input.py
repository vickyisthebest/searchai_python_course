from pathlib import Path
from datetime import datetime
import pandas as pd

def main():
    # Ask the user for keywords
    keywords_input = input("Enter your keywords, separated by commas: ")
    keywords = [kw.strip() for kw in keywords_input.split(",")]

    # Ask for location
    location = input("Enter the location (e.g., Barcelona, Spain): ")

    # Create a table (DataFrame) with dummy SERP data
    df = pd.DataFrame({
        "keyword": keywords,
        "location": [location] * len(keywords),
        "engine": ["google_traditional"] * len(keywords),
        "rank": [1] * len(keywords),
        "url": ["https://example.com"] * len(keywords),
    })

    # Print table to the screen
    print("\nHere’s your table:")
    print(df)

    # Prepare output path
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = reports_dir / f"report_{ts}.csv"

    # Save CSV
    df.to_csv(out_path, index=False)
    print(f"\nReport saved to: {out_path.resolve()}")

if __name__ == "__main__":
    main()
    

