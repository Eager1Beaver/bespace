# time_resolved_cca_analysis.py
from scipy.stats import entropy, skew, kurtosis
from config_loader import load_config
from logger import logger
from glob import glob
import pandas as pd
import numpy as np
import os

# Parameters
config = load_config()

OUTPUT_FOLDER = config.time_cca_params.output_dir  # "data/time_resolved_cca"
RESULTS_FOLDER = config.time_cca_params.results_dir  # "data/time_resolved_cca_analysis"

# Load all *_cca_timeseries.csv files
all_files = glob(os.path.join(OUTPUT_FOLDER, "*_cca_timeseries.csv"))
aggregated_data = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)

# Function 1: Stagewise mean and std of CCA1 and CCA2
stagewise_stats = aggregated_data.groupby("stage")[["cca_corr1", "cca_corr2"]].agg(["mean", "std", "count"])
stagewise_stats.columns = ['_'.join(col).strip() for col in stagewise_stats.columns.values]
stagewise_stats.reset_index(inplace=True)
stagewise_stats_path = os.path.join(RESULTS_FOLDER, "stagewise_summary.csv")
stagewise_stats.to_csv(stagewise_stats_path, index=False)
logger.info(f"Stagewise summary saved to {stagewise_stats_path}")

# Function 2: Compute temporal mean trajectories (binned over time)
aggregated_data["time_bin"] = pd.cut(aggregated_data["time_sec"], bins=np.arange(0, aggregated_data["time_sec"].max() + 600, 600))
trajectory = aggregated_data.groupby(["stage", "time_bin"])[["cca_corr1", "cca_corr2"]].mean().reset_index()
trajectory_path = os.path.join(RESULTS_FOLDER, "mean_cca_trajectory_by_stage.csv")
trajectory.to_csv(trajectory_path, index=False)
logger.info(f"Temporal mean trajectories saved to {trajectory_path}")

# Function 3: Compute subjectwise entropy of CCA1 and CCA2 per stage
def compute_entropy(x):
    hist, _ = np.histogram(x, bins=20, range=(0, 1), density=True)
    return entropy(hist + 1e-12)  # add small value to avoid log(0)

entropy_stats = (
    aggregated_data.groupby(["subject", "stage"])
    .agg({
        "cca_corr1": [compute_entropy, np.mean, np.std, skew, kurtosis],
        "cca_corr2": [compute_entropy, np.mean, np.std, skew, kurtosis]
    })
)

entropy_stats.columns = ['_'.join(col).strip() for col in entropy_stats.columns.values]
entropy_stats.reset_index(inplace=True)
entropy_stats_path = os.path.join(RESULTS_FOLDER, "entropy_by_subject_stage.csv")
entropy_stats.to_csv(entropy_stats_path, index=False)
logger.info(f"Entropy statistics saved to {entropy_stats_path}")

# Function 4: Save a few representative trajectories
sampled_subjects = aggregated_data["subject"].drop_duplicates().sample(3, random_state=42).tolist()
subset = aggregated_data[aggregated_data["subject"].isin(sampled_subjects)]
subset_path = os.path.join(RESULTS_FOLDER, "subset_trajectories.csv")
subset.to_csv(subset_path, index=False)
logger.info(f"Sample trajectories saved to {subset_path}")
