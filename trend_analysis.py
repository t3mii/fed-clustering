
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Set up folders
data_dir = Path("data")
output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)

# Load the existing clustered dataset
df = pd.read_csv(data_dir / "clustered_documents.csv")

df["publication_date"] = pd.to_datetime(
    df["publication_date"], errors="coerce"
)
df = df.dropna(subset=["publication_date", "cluster"]).copy()
df["year"] = df["publication_date"].dt.year
df = df[df["year"].between(2021, 2025)]

years = list(range(2021, 2026))
clusters = sorted(df["cluster"].unique())

# Labels based on our cluster inspection
cluster_names = {
    0: "Civil monetary penalties",
    1: "Aviation navigation",
    2: "Federal acquisition",
    3: "Aircraft safety",
    4: "Air quality",
    5: "Airport airspace",
    6: "Maritime safety",
    7: "Foreign sanctions",
    8: "Wildlife conservation",
    9: "Mixed regulatory topics"
}

def analyze_trends(data, name):
    # Count publications in each cluster each year
    counts = pd.crosstab(
        data["year"], data["cluster"]
    ).reindex(index=years, columns=clusters, fill_value=0)

    # Percentage of annual publications in each cluster
    totals = counts.sum(axis=1)
    shares = (
        counts.div(totals.replace(0, np.nan), axis=0)
        * 100
    ).fillna(0)

    # Calculate growth between 2021 and 2025
    summary = pd.DataFrame(index=clusters)
    summary.index.name = "cluster"

    summary["topic"] = [
        cluster_names.get(c, f"Cluster {c}")
        for c in clusters
    ]
    summary["count_2021"] = counts.loc[2021]
    summary["count_2025"] = counts.loc[2025]

    summary["growth_pct"] = (
        (summary["count_2025"] - summary["count_2021"])
        / summary["count_2021"].replace(0, np.nan)
        * 100
    )

    summary["share_2021"] = shares.loc[2021]
    summary["share_2025"] = shares.loc[2025]

    # Percentage-point change in annual share
    summary["share_change_pp"] = (
        summary["share_2025"] - summary["share_2021"]
    )

    # Trend across all five years
    summary["annual_share_slope"] = [
        np.polyfit(years, shares[c].values, 1)[0]
        for c in clusters
    ]

    summary = summary.sort_values(
        "share_change_pp", ascending=False
    )

    # Save all tables
    counts.to_csv(output_dir / f"{name}_yearly_counts.csv")
    shares.round(2).to_csv(
        output_dir / f"{name}_yearly_shares.csv"
    )
    summary.round(2).to_csv(
        output_dir / f"{name}_growth_summary.csv"
    )

  
    print("Total documents by year:")
    print(totals.to_string())
    print("\nGrowth ranking:")
    print(summary.round(2).to_string())

    # Plot five clusters with greatest share growth
    top_clusters = summary.head(5).index

    plt.figure(figsize=(10, 6))

    for cluster in top_clusters:
        plt.plot(
            years,
            shares[cluster],
            marker="o",
            linewidth=2,
            label=cluster_names.get(
                cluster, f"Cluster {cluster}"
            )
        )

    plt.title(f"Fastest-Growing Regulatory Topics: {name.title()}")
    plt.xlabel("Publication Year")
    plt.ylabel("Share of Annual Publications (%)")
    plt.xticks(years)
    plt.legend(fontsize=8)
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        output_dir / f"{name}_trend_chart.png",
        dpi=300
    )
    plt.close()

    return summary

# 1. Analyze all regulations
overall = analyze_trends(df, "overall")

# 2. Separate proposed and final rules
types = df["type"].astype(str).str.lower()

proposed = df[types.str.contains("propos", na=False)]
final = df[types.eq("rule") | types.str.contains("final", na=False)]

proposed_results = analyze_trends(proposed, "proposed")
final_results = analyze_trends(final, "final")
