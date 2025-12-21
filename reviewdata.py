from pathlib import Path
import json
import pandas as pd
from tqdm import tqdm
import kagglehub

# 1) Download / locate dataset
path = kagglehub.dataset_download("shivamparab/amazon-electronics-reviews")
data_file = Path(path) / "Electronics_5.json"

# huge file: can delete after done C:\Users\b3544\.cache\kagglehub\datasets\shivamparab\amazon-electronics-reviews\


print("Using file:", data_file)

# 2) Sample reviews (keep it manageable)
SAMPLE_N = 20000   # adjust later if needed

rows = []
with open(data_file, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(tqdm(f, desc="Reading reviews")):
        if i >= SAMPLE_N:
            break
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue

df = pd.DataFrame(rows)

# 3) Keep only what matters
print("\n--- DATA OVERVIEW ---")
print("Shape:", df.shape)
print("\nColumns:")
print(df.columns)

print("\nSample rows:")
print(df.head(3))

print("\nMissing values:")
print(df.isna().sum().sort_values(ascending=False).head(10))

print("\nRating distribution:")
print(df["overall"].value_counts(dropna=False))

print("\nReview length stats:")
print(df["reviewText"].str.len().describe())




df = df[
    ["asin", "reviewText", "overall", "summary", "reviewTime"]
].dropna(subset=["reviewText", "overall"])

df["overall"] = pd.to_numeric(df["overall"], errors="coerce")
df["reviewText"] = df["reviewText"].astype(str)
df["summary"] = df["summary"].astype(str)

# 4) Quick sanity checks
print("\nRows:", len(df))
print("Rating distribution:")
print(df["overall"].value_counts().sort_index())

# 5) Save sampled CSV for fast iteration
out_path = Path("data")
out_path.mkdir(exist_ok=True)

csv_path = out_path / f"electronics_sample_{len(df)}.csv"
df.to_csv(csv_path, index=False)

print("\nSaved sample to:", csv_path.resolve())
