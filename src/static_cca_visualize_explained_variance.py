# static_cca_visualize_explained_variance.py
from config_loader import load_config
import matplotlib.pyplot as plt
from logger import logger
import seaborn as sns
import pandas as pd
import os

# Parameters
config = load_config()

DATA_FOLDER = config.static_cca_params.output_dir  # "data/static_cca"
CSV_PATH = os.path.join(DATA_FOLDER, "explained_variance_by_stage.csv")
REPORT_FIGURES_FOLDER = config.report.figures_folder  # "report/figs"

df = pd.read_csv(CSV_PATH)

# Set plot style
sns.set(style="whitegrid")

# Boxplot for explained variance of EEG canonical projections (Xc)
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x="stage", y="explained_variance_Xc", hue="component", showmeans=True)
plt.title("Explained Variance of EEG Canonical Projections (Xc)")
plt.ylabel("Explained Variance Ratio")
plt.xlabel("Sleep Stage")
plt.legend(title="Component")
plt.ylim(0, 1)
plt.tight_layout()
fig_xc_path = os.path.join(REPORT_FIGURES_FOLDER, "figure5a_explained_variance_Xc.png")
plt.savefig(fig_xc_path)
plt.close()

# Boxplot for explained variance of EOG canonical projections (Yc)
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x="stage", y="explained_variance_Yc", hue="component", showmeans=True)
plt.title("Explained Variance of EOG Canonical Projections (Yc)")
plt.ylabel("Explained Variance Ratio")
plt.xlabel("Sleep Stage")
plt.legend(title="Component")
plt.ylim(0, 1)
plt.tight_layout()
fig_yc_path = os.path.join(REPORT_FIGURES_FOLDER, "figure5b_explained_variance_Yc.png")
plt.savefig(fig_yc_path)
plt.close()

logger.info(f"Saved explained variance plots to {REPORT_FIGURES_FOLDER}")
