import csv

# Open the CSV file for reading
with open("keywords.csv", "r", newline="") as csvfile:
    reader = csv.reader(csvfile)
    # Skip the header row
    next(reader)

    print("Here are the keywords you saved:")
    for row in reader:
        print(f"- {row[0]}")
