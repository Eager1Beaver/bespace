# stataic_cca_analyze_summary_stats.py
from config_loader import load_config
from scipy.stats import f_oneway
import matplotlib.pyplot as plt
from logger import logger
import seaborn as sns
import pandas as pd
import os

# Parameters
config = load_config()

OUTPUT_FOLDER = config.static_cca_params.output_dir # "data/static_cca"
RESULTS_FOLDER = config.static_cca_params.results_dir # "data/static_cca_analysis"

if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)

# Load summary CSV
summary_path = os.path.join(OUTPUT_FOLDER, "eeg_eog_cca_summary_stats.csv")
summary_df = pd.read_csv(summary_path)

logger.info("Summary stats loaded:", summary_df.shape)

# Plot distributions of CCA correlations
for var in ["cca_corr1", "cca_corr2"]:
    plt.figure(figsize=(8,5))
    sns.boxplot(x="stage", y=var, data=summary_df, showmeans=True)
    plt.title(f"Boxplot of {var} across sleep stages")
    plt.ylabel(var)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plot_path = os.path.join(RESULTS_FOLDER, f"{var}_boxplot_by_stage.png")
    plt.savefig(plot_path)
    plt.close()
    logger.info(f"Saved boxplot for {var}")

# Run ANOVA on CCA correlations
for var in ["cca_corr1", "cca_corr2"]:
    groups = []
    for stage in summary_df["stage"].unique():
        vals = summary_df.loc[summary_df["stage"]==stage, var].dropna().values
        if len(vals) > 1:
            groups.append(vals)
    if len(groups) > 1:
        stat, pval = f_oneway(*groups)
        logger.info(f"ANOVA for {var}: F={stat:.3f}, p={pval:.3e}")
    else:
        logger.warning(f"Not enough groups for ANOVA on {var}")

# Aggregate mean +- std for CCA correlations
agg = summary_df.groupby("stage")[["cca_corr1", "cca_corr2"]].agg(["mean", "std", "count"])
agg.columns = ['_'.join(col) for col in agg.columns]
agg.reset_index(inplace=True)
agg.to_csv(os.path.join(RESULTS_FOLDER, "cca_correlation_summary.csv"), index=False)
logger.info("Saved aggregated summary CSV for cca_corr1 and cca_corr2.")

# Analyze canonical projection means
projection_cols = [c for c in summary_df.columns if ("Xc" in c or "Yc" in c) and "_mean" in c]

for var in projection_cols:
    plt.figure(figsize=(8,5))
    sns.boxplot(x="stage", y=var, data=summary_df, showmeans=True)
    plt.title(f"Boxplot of {var} across sleep stages")
    plt.ylabel(var)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plot_path = os.path.join(RESULTS_FOLDER, f"{var}_boxplot_by_stage.png")
    plt.savefig(plot_path)
    plt.close()
    logger.info(f"Saved boxplot for {var}")
