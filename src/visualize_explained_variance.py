import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Re-define CSV path after kernel reset
csv_path = "data/static_cca/explained_variance_by_stage.csv"
df = pd.read_csv(csv_path)

# Create output folder
output_folder = "report/figs"
os.makedirs(output_folder, exist_ok=True)

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
fig_xc_path = os.path.join(output_folder, "figure5a_explained_variance_Xc.png")
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
fig_yc_path = os.path.join(output_folder, "figure5b_explained_variance_Yc.png")
plt.savefig(fig_yc_path)
plt.close()

