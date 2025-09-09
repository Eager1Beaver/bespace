# time_resolved_cca_plotting_groupped.py
from config_loader import load_config
import matplotlib.pyplot as plt
from logger import logger
import seaborn as sns
import pandas as pd
import os

# Parameters
config = load_config()

RESULTS_FOLDER = config.time_cca_params.results_dir  # "data/time_resolved_cca_analysis"
FIGURES_FOLDER = os.path.join(RESULTS_FOLDER, "figures")

if not os.path.exists(FIGURES_FOLDER):
    os.makedirs(FIGURES_FOLDER)

# Load the files
stagewise_summary = pd.read_csv(os.path.join(RESULTS_FOLDER, "stagewise_summary.csv"))
mean_cca_trajectory_by_stage = pd.read_csv(os.path.join(RESULTS_FOLDER, "mean_cca_trajectory_by_stage.csv"))
entropy_by_subject_stage = pd.read_csv(os.path.join(RESULTS_FOLDER, "entropy_by_subject_stage.csv"))
subset_trajectories = pd.read_csv(os.path.join(RESULTS_FOLDER, "subset_trajectories.csv"))

# 1. Boxplot of cca_corr1 and cca_corr2 by stage
plt.figure(figsize=(10, 6))
sns.boxplot(x='stage', y='cca_corr1', data=subset_trajectories)
plt.title('CCA Corr1 Distribution by Sleep Stage (Time-resolved)')
plt.savefig(os.path.join(FIGURES_FOLDER, "boxplot_cca_corr1_by_stage.png"))
plt.close()
logger.info("Saved boxplot of cca_corr1 by stage.")

plt.figure(figsize=(10, 6))
sns.boxplot(x='stage', y='cca_corr2', data=subset_trajectories)
plt.title('CCA Corr2 Distribution by Sleep Stage (Time-resolved)')
plt.savefig(os.path.join(FIGURES_FOLDER, "boxplot_cca_corr2_by_stage.png"))
plt.close()
logger.info("Saved boxplot of cca_corr2 by stage.")

# 2. Lineplot of mean trajectories per stage over time
plt.figure(figsize=(12, 6))
for stage in mean_cca_trajectory_by_stage['stage'].unique():
    stage_data = mean_cca_trajectory_by_stage[mean_cca_trajectory_by_stage['stage'] == stage]
    plt.plot(stage_data.index, stage_data['cca_corr1'], label=f"{stage} - CCA1")
plt.title("Mean CCA Corr1 Trajectory Over Time by Stage")
plt.xlabel("Time Bin Index")
plt.ylabel("CCA Corr1")
plt.legend()
plt.savefig(os.path.join(FIGURES_FOLDER, "trajectory_cca_corr1_by_stage.png"))
plt.close()
logger.info("Saved mean CCA Corr1 trajectory plot by stage.")

plt.figure(figsize=(12, 6))
for stage in mean_cca_trajectory_by_stage['stage'].unique():
    stage_data = mean_cca_trajectory_by_stage[mean_cca_trajectory_by_stage['stage'] == stage]
    plt.plot(stage_data.index, stage_data['cca_corr2'], label=f"{stage} - CCA2")
plt.title("Mean CCA Corr2 Trajectory Over Time by Stage")
plt.xlabel("Time Bin Index")
plt.ylabel("CCA Corr2")
plt.legend()
plt.savefig(os.path.join(FIGURES_FOLDER, "trajectory_cca_corr2_by_stage.png"))
plt.close()
logger.info("Saved mean CCA Corr2 trajectory plot by stage.")

# 3. Entropy values per stage for CCA1 and CCA2
plt.figure(figsize=(10, 6))
sns.boxplot(x='stage', y='cca_corr1_compute_entropy', data=entropy_by_subject_stage)
plt.title('CCA Corr1 Entropy by Sleep Stage')
plt.savefig(os.path.join(FIGURES_FOLDER, "entropy_cca_corr1_by_stage.png"))
plt.close()
logger.info("Saved entropy plot for CCA Corr1 by stage.")

plt.figure(figsize=(10, 6))
sns.boxplot(x='stage', y='cca_corr2_compute_entropy', data=entropy_by_subject_stage)
plt.title('CCA Corr2 Entropy by Sleep Stage')
plt.savefig(os.path.join(FIGURES_FOLDER, "entropy_cca_corr2_by_stage.png"))
plt.close()
logger.info("Saved entropy plot for CCA Corr2 by stage.")
