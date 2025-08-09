# generate_figures_report.py
from config_loader import load_config
import matplotlib.pyplot as plt
from logger import logger
import seaborn as sns
import pandas as pd
import os

# Parameters
config = load_config()

SUMMARY_FOLDER = config.static_cca_params.output_dir # "data/static_cca"
TIME_RESOLVED_RESULTS_FOLDER = config.time_cca_params.results_dir  # "data/time_resolved_cca_analysis"
REPORT_FIGURES_FOLDER = config.report.figures_folder  # "report/figs"

# Load data
summary_df = pd.read_csv(os.path.join(SUMMARY_FOLDER, "eeg_eog_cca_summary_stats.csv"))
subset_trajectories = pd.read_csv(os.path.join(TIME_RESOLVED_RESULTS_FOLDER, "subset_trajectories.csv"))
mean_cca_trajectory_by_stage = pd.read_csv(os.path.join(TIME_RESOLVED_RESULTS_FOLDER, "mean_cca_trajectory_by_stage.csv"))
entropy_by_subject_stage = pd.read_csv(os.path.join(TIME_RESOLVED_RESULTS_FOLDER, "entropy_by_subject_stage.csv"))

# Figure 1: Static CCA Boxplots
fig, axs = plt.subplots(1, 2, figsize=(12, 5))
sns.boxplot(x="stage", y="cca_corr1", data=summary_df, showmeans=True, ax=axs[0])
axs[0].set_title(r"Static CCA: $\rho_1$")
axs[0].set_ylabel("Correlation")
axs[0].grid(alpha=0.3)
axs[0].set_ylim(0,1)
fig.text(0.05, 0.95, 'Panel A', ha='left', va='center', rotation='horizontal', fontsize=12, fontweight='bold')

sns.boxplot(x="stage", y="cca_corr2", data=summary_df, showmeans=True, ax=axs[1])
axs[1].set_title(r"Static CCA: $\rho_2$")
#axs[1].set_ylabel("Correlation")
axs[1].grid(alpha=0.3)
axs[1].set_ylim(0,1)
axs[1].yaxis.set_visible(False)
fig.text(0.55, 0.95, 'Panel B', ha='left', va='center', rotation='horizontal', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(REPORT_FIGURES_FOLDER, "figure1_static_cca_boxplots.png"))
plt.close()
logger.info("Saved static CCA boxplots.")

# Figure 2: Time-resolved CCA Boxplots
fig, axs = plt.subplots(1, 2, figsize=(12, 5))
sns.boxplot(x='stage', y='cca_corr1', data=subset_trajectories, ax=axs[0])
axs[0].set_title(r'Time-Resolved CCA: $\rho_1$')
axs[0].set_ylabel("Correlation")
axs[0].grid(alpha=0.3)
axs[0].set_ylim(0,1)
fig.text(0.05, 0.95, 'Panel A', ha='left', va='center', rotation='horizontal', fontsize=12, fontweight='bold')

sns.boxplot(x='stage', y='cca_corr2', data=subset_trajectories, ax=axs[1])
axs[1].set_title(r'Time-Resolved CCA: $\rho_2$')
#axs[1].set_ylabel("Correlation")
axs[1].grid(alpha=0.3)
axs[1].set_ylim(0,1)
axs[1].yaxis.set_visible(False)
fig.text(0.55, 0.95, 'Panel B', ha='left', va='center', rotation='horizontal', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(REPORT_FIGURES_FOLDER, "figure2_time_resolved_boxplots.png"))
plt.close()
logger.info("Saved time-resolved CCA boxplots.")

# Figure 3: Mean Trajectories by Stage
fig, axs = plt.subplots(1, 2, figsize=(14, 5))
for stage in mean_cca_trajectory_by_stage['stage'].unique():
    data = mean_cca_trajectory_by_stage[mean_cca_trajectory_by_stage['stage'] == stage]
    axs[0].plot(data.index, data['cca_corr1'], label=stage)
    axs[1].plot(data.index, data['cca_corr2'], label=stage)

axs[0].set_title(r"Mean Trajectory: $\rho_1$")
axs[0].set_xlabel("Time Bin Index")
axs[0].set_ylabel("Correlation")
#axs[0].legend()
axs[0].grid(alpha=0.3)
axs[0].set_ylim(0,1)
fig.text(0.05, 0.9, 'Panel A', ha='left', va='center', rotation='horizontal', fontsize=12, fontweight='bold')

axs[1].set_title(r"Mean Trajectory: $\rho_2$")
axs[1].set_xlabel("Time Bin Index")
#axs[1].set_ylabel("Correlation")
#axs[1].legend()
axs[1].grid(alpha=0.3)
axs[1].set_ylim(0,1)
axs[1].yaxis.set_visible(False)
fig.text(0.55, 0.9, 'Panel B', ha='left', va='center', rotation='horizontal', fontsize=12, fontweight='bold')

handles, labels = axs[0].get_legend_handles_labels()

fig.legend(
    handles, labels,
    loc='lower center',
    ncol=len(labels),
    bbox_to_anchor=(0.5, 0.92),
    bbox_transform=fig.transFigure,
    frameon=False
)

# Leave extra space at bottom for legend
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(os.path.join(REPORT_FIGURES_FOLDER, "figure3_cca_trajectories.png"))
plt.close()
logger.info("Saved mean CCA trajectories by stage.")

# Figure 4: Entropy Boxplots
fig, axs = plt.subplots(1, 2, figsize=(12, 5))
sns.boxplot(x='stage', y='cca_corr1_compute_entropy', data=entropy_by_subject_stage, ax=axs[0])
axs[0].set_title(r"Entropy: $\rho_1$")
axs[0].set_ylabel("Entropy")
axs[0].grid(alpha=0.3)
axs[0].set_ylim(0,3)
fig.text(0.05, 0.95, 'Panel A', ha='left', va='center', rotation='horizontal', fontsize=12, fontweight='bold')

sns.boxplot(x='stage', y='cca_corr2_compute_entropy', data=entropy_by_subject_stage, ax=axs[1])
axs[1].set_title(r"Entropy: $\rho_2$")
#axs[1].set_ylabel("Entropy")
axs[1].grid(alpha=0.3)
axs[1].set_ylim(0,3)
axs[1].yaxis.set_visible(False)
fig.text(0.55, 0.95, 'Panel B', ha='left', va='center', rotation='horizontal', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(REPORT_FIGURES_FOLDER, "figure4_entropy_boxplots.png"))
plt.close()
logger.info("Saved entropy boxplots for CCA correlations.")
