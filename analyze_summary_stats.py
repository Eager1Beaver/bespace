import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import f_oneway, kruskal

# === PARAMETERS ===
data_folder = "data"
output_folder = "static_cca_analysis"

# --- Load summary CSV
summary_path = os.path.join(data_folder, "static_cca", "eeg_eog_cca_summary_stats.csv")
summary_df = pd.read_csv(summary_path)

print("Summary stats loaded:", summary_df.shape)

# --- Plot distributions of CCA correlations
for var in ["cca_corr1", "cca_corr2"]:
    plt.figure(figsize=(8,5))
    sns.boxplot(x="stage", y=var, data=summary_df, showmeans=True)
    plt.title(f"Boxplot of {var} across sleep stages")
    plt.ylabel(var)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plot_path = os.path.join(data_folder, output_folder, f"{var}_boxplot_by_stage.png")
    plt.savefig(plot_path)
    plt.close()
    print(f"Saved boxplot for {var}")

# --- Run ANOVA on CCA correlations
for var in ["cca_corr1", "cca_corr2"]:
    groups = []
    for stage in summary_df["stage"].unique():
        vals = summary_df.loc[summary_df["stage"]==stage, var].dropna().values
        if len(vals) > 1:
            groups.append(vals)
    if len(groups) > 1:
        stat, pval = f_oneway(*groups)
        print(f"ANOVA for {var}: F={stat:.3f}, p={pval:.3e}")
    else:
        print(f"Not enough groups for ANOVA on {var}")

# --- Aggregate mean ± std for CCA correlations
agg = summary_df.groupby("stage")[["cca_corr1", "cca_corr2"]].agg(["mean", "std", "count"])
agg.columns = ['_'.join(col) for col in agg.columns]
agg.reset_index(inplace=True)
agg.to_csv(os.path.join(data_folder, output_folder, "cca_correlation_summary.csv"), index=False)
print("Saved aggregated summary CSV for cca_corr1 and cca_corr2.")

# --- Optional: Analyze canonical projection means
projection_cols = [c for c in summary_df.columns if ("Xc" in c or "Yc" in c) and "_mean" in c]

for var in projection_cols:
    plt.figure(figsize=(8,5))
    sns.boxplot(x="stage", y=var, data=summary_df, showmeans=True)
    plt.title(f"Boxplot of {var} across sleep stages")
    plt.ylabel(var)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plot_path = os.path.join(data_folder, output_folder, f"{var}_boxplot_by_stage.png")
    plt.savefig(plot_path)
    plt.close()
    print(f"Saved boxplot for {var}")
