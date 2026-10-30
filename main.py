import requests
import pandas as pd
import time
from datetime import date
from calendar import monthrange



from sklearn.feature_extraction.text import TfidfVectorizer

df = pd.read_csv("federal_register_documents.csv")

# Handle missing abstracts without discarding documents
df["abstract"] = df["abstract"].fillna("")

# Combine title and abstract
df["combined_text"] = (
    df["title"].fillna("") + " " + df["abstract"]
)

# Remove any accidental empty text records
df = df[df["combined_text"].str.strip() != ""].copy()

# Extract year for later trend analysis
df["publication_date"] = pd.to_datetime(df["publication_date"])
df["year"] = df["publication_date"].dt.year

# Convert text into TF-IDF features
vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),
    min_df=5,
    max_df=0.85,
    max_features=30000
)

X = vectorizer.fit_transform(df["combined_text"])

print("Documents:", X.shape[0])
print("TF-IDF features:", X.shape[1])
print("Matrix type:", type(X))

from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score

results = []

for k in range(3, 11):

    model = MiniBatchKMeans(
        n_clusters=k,
        random_state=42,
        batch_size=1024,
        n_init=10
    )

    labels = model.fit_predict(X)

    score = silhouette_score(
        X,
        labels,
        metric="cosine",
        sample_size=2500,
        random_state=42
    )

    results.append({
        "k": k,
        "silhouette_score": score
    })

    print(f"k={k}, silhouette score={score:.4f}")

results_df = pd.DataFrame(results)

print("\nComparison:")
print(results_df.sort_values(
    "silhouette_score", ascending=False
))