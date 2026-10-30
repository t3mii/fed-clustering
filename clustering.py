
import pandas as pd
import joblib
from pathlib import Path
from scipy.sparse import load_npz
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score

# Load saved files
DATA_PATH = Path("data")

df = pd.read_csv(DATA_PATH / "processed_documents.csv")
X = load_npz(DATA_PATH / "tfidf_matrix.npz")

results = []
models = {}

# Test different numbers of clusters
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

    models[k] = model

    print(f"k={k}, silhouette={score:.4f}")

# Save comparison results
results_df = pd.DataFrame(results)
results_df.to_csv(DATA_PATH / "cluster_comparison.csv", index=False)

# Select the best-performing k
best_k = results_df.loc[
    results_df["silhouette_score"].idxmax(), "k"
]

best_k = int(best_k)
best_model = models[best_k]

# Assign cluster labels
df["cluster"] = best_model.labels_

# Save clustered documents and model
df.to_csv(DATA_PATH / "clustered_documents.csv", index=False)
joblib.dump(best_model, DATA_PATH / "best_clustering_model.pkl")

print("\nBest number of clusters:", best_k)
print("\nCluster sizes:")
print(df["cluster"].value_counts().sort_index())

print("\nSaved clustered documents!")
