import os
import pandas as pd
import numpy as np
from scipy.stats import entropy, skew, kurtosis
from glob import glob

# Define path to CCA timeseries files
data_folder = "data/time_resolved_cca"
output_folder = "data/time_resolved_cca_analysis"
os.makedirs(output_folder, exist_ok=True)

# Load all *_cca_timeseries.csv files
all_files = glob(os.path.join(data_folder, "*_cca_timeseries.csv"))
aggregated_data = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)

# Function 1: Stagewise mean and std of CCA1 and CCA2
stagewise_stats = aggregated_data.groupby("stage")[["cca_corr1", "cca_corr2"]].agg(["mean", "std", "count"])
stagewise_stats.columns = ['_'.join(col).strip() for col in stagewise_stats.columns.values]
stagewise_stats.reset_index(inplace=True)
stagewise_stats.to_csv(os.path.join(output_folder, "stagewise_summary.csv"), index=False)

# Function 2: Compute temporal mean trajectories (binned over time)
aggregated_data["time_bin"] = pd.cut(aggregated_data["time_sec"], bins=np.arange(0, aggregated_data["time_sec"].max() + 600, 600))
trajectory = aggregated_data.groupby(["stage", "time_bin"])[["cca_corr1", "cca_corr2"]].mean().reset_index()
trajectory.to_csv(os.path.join(output_folder, "mean_cca_trajectory_by_stage.csv"), index=False)

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
entropy_stats.to_csv(os.path.join(output_folder, "entropy_by_subject_stage.csv"), index=False)

# Function 4: Save a few representative trajectories (handpicked or automatic later)
sampled_subjects = aggregated_data["subject"].drop_duplicates().sample(3, random_state=42).tolist()
subset = aggregated_data[aggregated_data["subject"].isin(sampled_subjects)]
subset.to_csv(os.path.join(output_folder, "subset_trajectories.csv"), index=False)