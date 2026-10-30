import pandas as pd
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import save_npz
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


DATA_PATH = Path("data/federal_register_documents.csv")
OUTPUT_PATH = Path("data")

def preprocess_data():

    df = pd.read_csv(DATA_PATH)

    df["abstract"] = df["abstract"].fillna("")
    df["combined_text"] = df["title"] + " " + df["abstract"]

    df["publication_date"] = pd.to_datetime(
        df["publication_date"]
    )
    df["year"] = df["publication_date"].dt.year

    df = df[df["combined_text"].str.strip() != ""].copy()


    # Common Federal Register and regulatory language
    custom_stopwords = {
        "rule", "rules", "regulation", "regulations",
        "federal", "department", "commission",
        "final", "proposed", "document",
        "act", "pursuant", "hereby",
        "thereof", "therein", "accordance",
        "applicable", "authority", "amendment",
        "amendments", "part", "section",
        "sections", "subpart", "paragraph"
    }

    all_stopwords = list(ENGLISH_STOP_WORDS.union(custom_stopwords))

    vectorizer = TfidfVectorizer(
        stop_words=all_stopwords,
        ngram_range=(1, 2),
        min_df=5,
        max_df=0.85,
        max_features=30000
    )

    X = vectorizer.fit_transform(df["combined_text"])


    # Save processed data
    df.to_csv(OUTPUT_PATH / "processed_documents.csv", index=False)

    # Save TF-IDF matrix
    save_npz(OUTPUT_PATH / "tfidf_matrix.npz", X)

    # Save vectorizer
    joblib.dump(vectorizer, OUTPUT_PATH / "tfidf_vectorizer.pkl")

    print("Preprocessing complete!")
    print("Documents:", X.shape[0])
    print("Features:", X.shape[1])


if __name__ == "__main__":
    preprocess_data()