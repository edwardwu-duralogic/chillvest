from pathlib import Path
import json
import re
import pandas as pd
from tqdm import tqdm
import kagglehub

# -----------------------------
# Project paths (portable: script OR notebook)
# Create consistent project and data folders so outputs always save to the same place.
# -----------------------------
try:
    PROJECT_ROOT = Path(__file__).resolve().parent
except NameError:
    PROJECT_ROOT = Path.cwd()

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# -----------------------------
# 1) Download / locate dataset
# Download (or reuse cached) Amazon Electronics reviews and locate the raw JSON review file.
# -----------------------------
path = kagglehub.dataset_download("shivamparab/amazon-electronics-reviews")
data_file = Path(path) / "Electronics_5.json"
print("Using file:", data_file)

# -----------------------------
# 2) Sample reviews (keep it manageable)
# Load a manageable sample of reviews quickly so we can iterate fast before scaling up.
# Note: This is not random sampling; it’s “first N” sampling.
# -----------------------------
SAMPLE_N = 20000  # bump later (50k-200k) once pipeline is stable

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
# Shift + Enter for running selected lines.

# Inspect schema to confirm what fields are available before building analysis features.
print("\n--- DATA OVERVIEW ---")
print("Shape:", df.shape)
print("Columns:", list(df.columns))

# -----------------------------
# 3) Keep columns that matter for merchant insights
# Keep only the review fields that support SKU-level diagnosis, trend analysis, and noise control.
# -----------------------------
keep_cols = [
    "asin",
    "reviewText",
    "overall",
    "summary",
    "reviewTime",
    "unixReviewTime",
    "verified",
    "helpful",
    "reviewerID",
]
existing_keep_cols = [c for c in keep_cols if c in df.columns]
df = df[existing_keep_cols].copy()
# df[...] creates a new DataFrame view-like object (sometimes a view, sometimes a copy — pandas can be ambiguous)
# .copy() forces it to be a real independent copy in memory
# df = ... reassigns the variable name df to that new object → so your old df object becomes unreferenced and can be garbage-collected

# -----------------------------
# 4) Clean / coerce types
# Clean core fields and combine title+body into one text column for consistent NLP analysis.
# -----------------------------
if "reviewText" in df.columns:
    df = df.dropna(subset=["reviewText"])
    df["reviewText"] = df["reviewText"].astype(str)

if "overall" in df.columns:
    df["overall"] = pd.to_numeric(df["overall"], errors="coerce")
    df = df.dropna(subset=["overall"])

if "summary" in df.columns:
    df["summary"] = df["summary"].fillna("").astype(str)

# unify text field for NLP
df["text"] = (df.get("summary", "") + " " + df["reviewText"]).str.strip()

# parse time (best effort)
# Convert review timestamps into a usable date field so we can detect issue trends over time.
if "unixReviewTime" in df.columns:
    df["review_dt"] = pd.to_datetime(df["unixReviewTime"], unit="s", errors="coerce")
elif "reviewTime" in df.columns:
    df["review_dt"] = pd.to_datetime(df["reviewTime"], errors="coerce")
else:
    df["review_dt"] = pd.NaT

# pd.to_datetime([0, 1, "bad"], unit="s", errors="coerce")
# # -> 1970-01-01 00:00:00
# # -> 1970-01-01 00:00:01
# # -> NaT

# helpful votes (format sometimes like [x, y])
# Extract helpful upvotes to later weight which complaints are most credible and impactful.
if "helpful" in df.columns:
    def helpful_upvotes(x):
        if isinstance(x, (list, tuple)) and len(x) >= 1:
            return x[0]
        return None
    df["helpful_upvotes"] = df["helpful"].apply(helpful_upvotes)

# -----------------------------
# 5) Merchant-grade derived features (Week 5)
# Create interpretable text-derived signals (intensity and return intent) to quantify complaint severity.
# -----------------------------
def uppercase_ratio(s: str) -> float:
    letters = [c for c in s if c.isalpha()]
    if not letters:
        return 0.0
    uppers = sum(1 for c in letters if c.isupper())
    return uppers / len(letters)

df["review_len"] = df["text"].str.len()
df["word_count"] = df["text"].str.split().str.len()
df["exclaim_count"] = df["text"].str.count("!")
df["question_count"] = df["text"].str.count(r"\?")
df["uppercase_ratio"] = df["text"].apply(uppercase_ratio)
df["has_return_language"] = df["text"].str.contains(r"\b(return|refund|sent back|rma)\b", flags=re.I, regex=True)

# rating buckets (merchant lens)
# Segment customers into unhappy/neutral/happy buckets so we can isolate failure modes vs value drivers.
df["rating_bucket"] = pd.cut(
    df["overall"],
    bins=[0, 2, 3, 5],
    labels=["low_1_2", "mid_3", "high_4_5"],
    include_lowest=True,
)
# pd.cut creates intervals:
    # Bin 1: (0, 2] <- <0 AND <=2
    # Bin 2: (2, 3]
    # Bin 3: (3, 5]
    # include_lowest=True makes the first bin include 0, so:
    # Bin 1 becomes [0, 2]

# -----------------------------
# 6) Quick sanity checks
# Validate that the cleaned dataset still looks reasonable before generating insights tables.
# -----------------------------
print("\n--- SANITY CHECKS ---")
print("Rows:", len(df))
print("Rating distribution:\n", df["overall"].value_counts().sort_index())
print("\nBucket distribution:\n", df["rating_bucket"].value_counts(dropna=False))

# -----------------------------
# 7) Merchant tables using TF-IDF (top complaint/value drivers)
# Extract the most salient words/phrases for any review segment using TF-IDF as a fast theme detector.
# -----------------------------
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def top_terms_for_mask(mask, top_n=25, min_df=5):
# mask is a boolean Series: True/False for each row
# df.loc[mask, "text"] keeps only rows where mask is True, and only the text column
# .dropna() removes missing text values
# So if mask = “low ratings”, sub becomes all the low-rating review texts.
    sub = df.loc[mask, "text"].dropna()
    if len(sub) < 200: # TF-IDF is unstable if there's only a few reviews. This prevents junk outputs.
        return pd.DataFrame({"term": [], "score": []})

    vec = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=min_df,
        max_df=0.9
    )
# stop_words="english"
    # removes common words like “the”, “and”
    # otherwise they dominate results and are useless
# ngram_range=(1, 2)
    # considers single words (“battery”) and two-word phrases (“battery life”)
    # phrases are far more merchant-relevant than single tokens
# min_df=min_df (default 5)
    # ignore terms that appear in fewer than 5 reviews in this subset
    # helps avoid one-off weirdness
# max_df=0.9
    # ignore terms that appear in >90% of reviews in this subset
    # because they’re not discriminative (too common)

    X = vec.fit_transform(sub)
        # This outputs a sparse matrix:
            # Rows = reviews
            # Columns = terms/phrases
            # Values = TF-IDF score for that term in that review
            # Shape example:
                #15,000 reviews × 40,000 terms
    scores = np.asarray(X.mean(axis=0)).ravel() 
        # X.mean(axis=0) averages each column across all reviews
        # gives “on average, how important is term T in this subset?”
    terms = np.array(vec.get_feature_names_out()) # terms[j] corresponds to scores[j]
    top_idx = scores.argsort()[::-1][:top_n]
        #  argsort() returns indices sorted from low→high
        # [::-1] flips to high→low
        # [:top_n] takes top N
    return pd.DataFrame({"term": terms[top_idx], "score": scores[top_idx]})



# Identify top complaint themes from low ratings and top value themes from high ratings.
low_mask = df["rating_bucket"].eq("low_1_2")
high_mask = df["rating_bucket"].eq("high_4_5")

complaint_drivers = top_terms_for_mask(low_mask, top_n=30)
value_drivers = top_terms_for_mask(high_mask, top_n=30)

# Short Symmary:
    # TF-IDF tells:
        # what terms are salient in that group
    # TF-IDF does NOT tell you:
        # causality
        # impact magnitude (without linking to outcomes like returns or rating delta)
        # that a term is unique to this group (unless you compare groups)


# unmet needs detection: "wish / would / should / could"
# Detect future feature requests and missing expectations by analyzing desire-language in reviews.
unmet_mask = df["text"].str.contains(r"\b(wish|would|should|could|if only|needs to)\b", flags=re.I, regex=True)
unmet_needs_terms = top_terms_for_mask(unmet_mask & high_mask, top_n=30, min_df=3)  # "opportunities" inside satisfied users
unmet_needs_terms_low = top_terms_for_mask(unmet_mask & low_mask, top_n=30, min_df=3)  # "missing expectations" in unhappy users

# -----------------------------
# 8) Trend: complaint bucket share by month (if time exists)
# Track the monthly share of bad/neutral/good reviews to detect quality or satisfaction shifts over time.
# -----------------------------
trend = None
if df["review_dt"].notna().any():
    df["year_month"] = df["review_dt"].dt.to_period("M").astype(str)
    trend = (
        df.groupby(["year_month", "rating_bucket"])
          .size()
          .reset_index(name="n")
    )
    trend["share"] = trend.groupby("year_month")["n"].transform(lambda x: x / x.sum())
    trend = trend.sort_values(["year_month", "rating_bucket"])

# -----------------------------
# 9) Save artifacts for fast iteration
# Save cleaned data and insight tables as files so analysis is reproducible and easy to reuse.
# -----------------------------
OUTPUT_FILE = DATA_DIR / "electronics_sample.csv"
df.to_csv(OUTPUT_FILE, index=False)

complaint_drivers_file = DATA_DIR / "complaint_drivers_low_1_2.csv"
value_drivers_file = DATA_DIR / "value_drivers_high_4_5.csv"
unmet_high_file = DATA_DIR / "unmet_needs_from_happy.csv"
unmet_low_file = DATA_DIR / "unmet_needs_from_unhappy.csv"

complaint_drivers.to_csv(complaint_drivers_file, index=False)
value_drivers.to_csv(value_drivers_file, index=False)
unmet_needs_terms.to_csv(unmet_high_file, index=False)
unmet_needs_terms_low.to_csv(unmet_low_file, index=False)

if trend is not None:
    trend_file = DATA_DIR / "trend_bucket_share_by_month.csv"
    trend.to_csv(trend_file, index=False)
    print("\nSaved trend table:", trend_file.resolve())

# Preview the extracted themes to quickly verify they make sense before deeper analysis.
print("\nSaved sample to:", OUTPUT_FILE.resolve())
print("Saved complaint drivers:", complaint_drivers_file.resolve())
print("Saved value drivers:", value_drivers_file.resolve())
print("Saved unmet needs (happy):", unmet_high_file.resolve())
print("Saved unmet needs (unhappy):", unmet_low_file.resolve())

print("\n--- TOP COMPLAINT DRIVERS (LOW RATINGS) ---")
print(complaint_drivers.head(15).to_string(index=False))

print("\n--- TOP VALUE DRIVERS (HIGH RATINGS) ---")
print(value_drivers.head(15).to_string(index=False))

print("\n--- UNMET NEEDS (FROM HAPPY USERS) ---")
print(unmet_needs_terms.head(15).to_string(index=False))

print("\n--- UNMET NEEDS (FROM UNHAPPY USERS) ---")
print(unmet_needs_terms_low.head(15).to_string(index=False))



# from pathlib import Path
# import json
# import pandas as pd
# from tqdm import tqdm
# import kagglehub

# # -----------------------------
# # Project paths (portable)
# # -----------------------------
# PROJECT_ROOT = Path(__file__).resolve().parent
# DATA_DIR = PROJECT_ROOT / "data"
# DATA_DIR.mkdir(exist_ok=True)

# # 1) Download / locate dataset
# path = kagglehub.dataset_download("shivamparab/amazon-electronics-reviews")
# data_file = Path(path) / "Electronics_5.json"

# # huge file lives under:
# # C:\Users\b3544\.cache\kagglehub\datasets\shivamparab\amazon-electronics-reviews\
# print("Using file:", data_file)

# # 2) Sample reviews (keep it manageable)
# SAMPLE_N = 20000  # adjust later if needed

# rows = []
# with open(data_file, "r", encoding="utf-8", errors="ignore") as f:
#     for i, line in enumerate(tqdm(f, desc="Reading reviews")):
#         if i >= SAMPLE_N:
#             break
#         try:
#             rows.append(json.loads(line))
#         except json.JSONDecodeError:
#             continue

# df = pd.DataFrame(rows)

# # 3) Data overview (before selecting columns)
# print("\n--- DATA OVERVIEW ---")
# print("Shape:", df.shape)
# print("\nColumns:")
# print(df.columns)

# print("\nSample rows:")
# print(df.head(3))

# print("\nMissing values:")
# print(df.isna().sum().sort_values(ascending=False).head(10))

# print("\nRating distribution:")
# print(df["overall"].value_counts(dropna=False) if "overall" in df.columns else "No 'overall' column found")

# print("\nReview length stats:")
# print(df["reviewText"].str.len().describe() if "reviewText" in df.columns else "No 'reviewText' column found")

# # Keep only what matters (defensive: only keep columns that exist)
# keep_cols = ["asin", "reviewText", "overall", "summary", "reviewTime"]
# existing_keep_cols = [c for c in keep_cols if c in df.columns]
# df = df[existing_keep_cols].copy()

# # Clean / coerce types
# if "reviewText" in df.columns:
#     df = df.dropna(subset=["reviewText"])
#     df["reviewText"] = df["reviewText"].astype(str)

# if "overall" in df.columns:
#     df["overall"] = pd.to_numeric(df["overall"], errors="coerce")
#     df = df.dropna(subset=["overall"])

# if "summary" in df.columns:
#     df["summary"] = df["summary"].fillna("").astype(str)

# # 4) Quick sanity checks
# print("\n--- SANITY CHECKS ---")
# print("Rows:", len(df))
# if "overall" in df.columns:
#     print("Rating distribution:")
#     print(df["overall"].value_counts().sort_index())

# # 5) Save sampled CSV for fast iteration (4.2: overwrite one canonical file)
# OUTPUT_FILE = DATA_DIR / "electronics_sample.csv"

# if OUTPUT_FILE.exists():
#     print(f"\nOverwriting existing sample file: {OUTPUT_FILE}")

# df.to_csv(OUTPUT_FILE, index=False)
# print("\nSaved sample to:", OUTPUT_FILE.resolve())





