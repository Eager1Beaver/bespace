# static_cca_analyze_canonical_projections.py
from scipy.stats import skew, kurtosis, f_oneway
from config_loader import load_config
import matplotlib.pyplot as plt
from logger import logger
import seaborn as sns
import pandas as pd
import numpy as np
import glob
import os

# TODO: plot are not necessary - remove

# Parameters
config = load_config()

OUTPUT_FOLDER = config.static_cca_params.output_dir # "data/static_cca"
RESULTS_FOLDER = config.static_cca_params.results_dir # "data/static_cca_analysis"
FIGURES_FOLDER = os.path.join(RESULTS_FOLDER, "figures")

if not os.path.exists(FIGURES_FOLDER):
    os.makedirs(FIGURES_FOLDER)

if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)

# File patterns
pattern_Xc = os.path.join(OUTPUT_FOLDER, "*_Xc_downsampled.csv")
pattern_Yc = os.path.join(OUTPUT_FOLDER, "*_Yc_downsampled.csv")

# Projection loader
def load_projection_files(pattern, prefix):
    rows = []
    for filepath in glob.glob(pattern):
        filename = os.path.basename(filepath)
        
        name_parts = filename.replace("_Xc_downsampled.csv", "") \
                             .replace("_Yc_downsampled.csv", "").split("_")
        
        if len(name_parts) != 2:
            logger.warning(f"Skipping unexpected filename: {filename}")
            continue
        
        subject, stage = name_parts

        df = pd.read_csv(filepath)

        # Unpivoting the dataframe
        df_long = df.melt(var_name="projection", value_name="value")
        df_long["subject"] = subject
        df_long["stage"] = stage
        df_long["type"] = prefix

        rows.append(df_long)

    if rows:
        return pd.concat(rows, ignore_index=True)
    else:
        return pd.DataFrame(columns=["subject", "stage", "projection", "value", "type"])

# Load all downsampled files
df_Xc = load_projection_files(pattern_Xc, "Xc")
df_Yc = load_projection_files(pattern_Yc, "Yc")

all_data = pd.concat([df_Xc, df_Yc], ignore_index=True)
logger.info(f"Loaded downsampled projections: {all_data.shape}")

if all_data.empty:
    logger.warning("No data loaded! Check file paths and patterns.")
    exit()

# Save combined file
#all_data.to_csv(os.path.join(OUTPUT_FOLDER, "all_downsampled_projections.csv"), index=False)
#logger.info("Saved combined downsampled data.")

# Compute summary statistics by stage and projection
summary_rows = []
for proj_type in ["Xc", "Yc"]:
    for comp in ["1", "2"]:
        projection_name = f"{proj_type}_{comp}"
        df_proj = all_data[
            (all_data["type"] == proj_type) &
            (all_data["projection"] == projection_name)
        ]
        if df_proj.empty:
            continue

        grouped = df_proj.groupby("stage")["value"]
        for stage, vals in grouped:
            summary_rows.append({
                "projection": projection_name,
                "stage": stage,
                "mean": np.mean(vals),
                "std": np.std(vals),
                "skewness": skew(vals),
                "kurtosis": kurtosis(vals),
                "count": len(vals)
            })

summary_df = pd.DataFrame(summary_rows)
summary_csv = os.path.join(RESULTS_FOLDER, "canonical_projection_summary_by_stage.csv")
summary_df.to_csv(summary_csv, index=False)
logger.info(f"Saved summary stats to {summary_csv}")

# Run ANOVA across stages
for proj_type in ["Xc", "Yc"]:
    for comp in ["1", "2"]:
        projection_name = f"{proj_type}_{comp}"
        df_proj = all_data[
            (all_data["type"] == proj_type) &
            (all_data["projection"] == projection_name)
        ]
        if df_proj.empty:
            continue

        groups = [g["value"].values for _, g in df_proj.groupby("stage")]
        if len(groups) > 1:
            fval, pval = f_oneway(*groups)
            logger.info(f"ANOVA for {projection_name}: F = {fval:.3f}, p = {pval:.3e}")

# TODO: deprecate below
# Plot distributions per stage and projection
for proj_type in ["Xc", "Yc"]:
    for comp in ["1", "2"]:
        projection_name = f"{proj_type}_{comp}"

        df_plot = all_data[
            (all_data["type"] == proj_type) &
            (all_data["projection"] == projection_name)
        ]

        if df_plot.empty:
            logger.warning(f"No data for {projection_name}")
            continue

        # KDE Plot
        plt.figure(figsize=(10,5))
        sns.kdeplot(
            data=df_plot,
            x="value",
            hue="stage",
            common_norm=False,
            fill=True,
            alpha=0.3,
            linewidth=1.5
        )
        plt.title(f"Density of {projection_name} across stages")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_FOLDER, f"{projection_name}_kde.png"))
        plt.close()
        logger.info(f"Saved density plot for {projection_name}")

        # Boxplot
        plt.figure(figsize=(8,5))
        sns.boxplot(
            x="stage",
            y="value",
            data=df_plot,
            showmeans=True
        )
        plt.title(f"Boxplot of {projection_name} across stages")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_FOLDER, f"{projection_name}_boxplot.png"))
        plt.close()
        logger.info(f"Saved boxplot for {projection_name}")
        