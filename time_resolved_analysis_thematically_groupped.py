import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load the files
stagewise_summary = pd.read_csv("data/time_resolved_cca_analysis/stagewise_summary.csv")
mean_cca_trajectory_by_stage = pd.read_csv("data/time_resolved_cca_analysis/mean_cca_trajectory_by_stage.csv")
entropy_by_subject_stage = pd.read_csv("data/time_resolved_cca_analysis/entropy_by_subject_stage.csv")
subset_trajectories = pd.read_csv("data/time_resolved_cca_analysis/subset_trajectories.csv")

# Prepare to generate figures and save them
figures_folder = "data/time_resolved_cca_analysis/figures"
os.makedirs(figures_folder, exist_ok=True)

# 1. Boxplot of cca_corr1 and cca_corr2 by stage
plt.figure(figsize=(10, 6))
sns.boxplot(x='stage', y='cca_corr1', data=subset_trajectories)
plt.title('CCA Corr1 Distribution by Sleep Stage (Time-resolved)')
plt.savefig(os.path.join(figures_folder, "boxplot_cca_corr1_by_stage.png"))
plt.close()

plt.figure(figsize=(10, 6))
sns.boxplot(x='stage', y='cca_corr2', data=subset_trajectories)
plt.title('CCA Corr2 Distribution by Sleep Stage (Time-resolved)')
plt.savefig(os.path.join(figures_folder, "boxplot_cca_corr2_by_stage.png"))
plt.close()

# 2. Lineplot of mean trajectories per stage over time
plt.figure(figsize=(12, 6))
for stage in mean_cca_trajectory_by_stage['stage'].unique():
    stage_data = mean_cca_trajectory_by_stage[mean_cca_trajectory_by_stage['stage'] == stage]
    plt.plot(stage_data.index, stage_data['cca_corr1'], label=f"{stage} - CCA1")
plt.title("Mean CCA Corr1 Trajectory Over Time by Stage")
plt.xlabel("Time Bin Index")
plt.ylabel("CCA Corr1")
plt.legend()
plt.savefig(os.path.join(figures_folder, "trajectory_cca_corr1_by_stage.png"))
plt.close()

plt.figure(figsize=(12, 6))
for stage in mean_cca_trajectory_by_stage['stage'].unique():
    stage_data = mean_cca_trajectory_by_stage[mean_cca_trajectory_by_stage['stage'] == stage]
    plt.plot(stage_data.index, stage_data['cca_corr2'], label=f"{stage} - CCA2")
plt.title("Mean CCA Corr2 Trajectory Over Time by Stage")
plt.xlabel("Time Bin Index")
plt.ylabel("CCA Corr2")
plt.legend()
plt.savefig(os.path.join(figures_folder, "trajectory_cca_corr2_by_stage.png"))
plt.close()

# 3. Entropy values per stage for CCA1 and CCA2
plt.figure(figsize=(10, 6))
sns.boxplot(x='stage', y='cca_corr1_compute_entropy', data=entropy_by_subject_stage)
plt.title('CCA Corr1 Entropy by Sleep Stage')
plt.savefig(os.path.join(figures_folder, "entropy_cca_corr1_by_stage.png"))
plt.close()

plt.figure(figsize=(10, 6))
sns.boxplot(x='stage', y='cca_corr2_compute_entropy', data=entropy_by_subject_stage)
plt.title('CCA Corr2 Entropy by Sleep Stage')
plt.savefig(os.path.join(figures_folder, "entropy_cca_corr2_by_stage.png"))
plt.close()
