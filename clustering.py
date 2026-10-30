import pandas as pd
import joblib
from scipy.sparse import load_npz

df = pd.read_csv("data/processed_documents.csv")
X = load_npz("data/tfidf_matrix.npz")
vectorizer = joblib.load("data/tfidf_vectorizer.pkl")