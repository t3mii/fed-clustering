
import pandas as pd
import joblib
from pathlib import Path
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = Path("data")

# Load saved data and models
df = pd.read_csv(DATA_PATH / "clustered_documents.csv")
X = load_npz(DATA_PATH / "tfidf_matrix.npz")

model = joblib.load(DATA_PATH / "best_clustering_model.pkl")
vectorizer = joblib.load(DATA_PATH / "tfidf_vectorizer.pkl")

feature_names = vectorizer.get_feature_names_out()

# Inspect each cluster
for cluster_id in range(model.n_clusters):

    print("\n" + "=" * 70)
    print(f"CLUSTER {cluster_id}")
    print("=" * 70)

    # Find the most important terms
    center = model.cluster_centers_[cluster_id]

    top_indices = center.argsort()[-15:][::-1]
    top_terms = feature_names[top_indices]

    print("\nTop 15 terms:")
    print(", ".join(top_terms))

    # Find documents belonging to this cluster
    cluster_indices = df.index[
        df["cluster"] == cluster_id
    ].tolist()

    # Find documents closest to the cluster center
    cluster_matrix = X[cluster_indices]

    similarities = cosine_similarity(
        cluster_matrix,
        center.reshape(1, -1)
    ).flatten()

    # Select the five most representative documents
    top_positions = similarities.argsort()[-5:][::-1]

    print("\nRepresentative documents:")

    for position in top_positions:
        doc_index = cluster_indices[position]
        document = df.loc[doc_index]

        print("\nTitle:", document["title"])
        print("Date:", document["publication_date"])
        print("Abstract:", str(document["abstract"])[:350])
