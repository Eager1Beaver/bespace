# static_cca_explained_variance.py
from config_loader import load_config
from logger import logger
import pandas as pd
import numpy as np
import os

# Parameters
config = load_config()

DATA_FOLDER = config.static_cca_params.output_dir  # "data/static_cca"
OUTPUT_PATH = os.path.join(DATA_FOLDER, "explained_variance_by_stage.csv")

# Find files
xc_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith("_Xc_downsampled.csv")]
yc_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith("_Yc_downsampled.csv")]

# Get stage and subject
def parse_metadata(filename):
    parts = filename.replace("_Xc_downsampled.csv", "").replace("_Yc_downsampled.csv", "").split("_")
    if len(parts) == 2:
        return parts[0], parts[1]
    return "unknown", "unknown"

# Initialize
records = []

for xc_file in xc_files:
    base = xc_file.replace("_Xc_downsampled.csv", "")
    yc_file = base + "_Yc_downsampled.csv"
    xc_path = os.path.join(DATA_FOLDER, xc_file)
    yc_path = os.path.join(DATA_FOLDER, yc_file)

    if not os.path.exists(yc_path):
        continue

    subject, stage = parse_metadata(xc_file)
    try:
        Xc = pd.read_csv(xc_path).values
        Yc = pd.read_csv(yc_path).values

        if Xc.shape[0] != Yc.shape[0]:
            continue

        var_Xc = np.var(Xc, axis=0)
        var_Yc = np.var(Yc, axis=0)

        total_var_X = var_Xc.sum()
        total_var_Y = var_Yc.sum()

        for i in range(2):
            records.append({
                "subject": subject,
                "stage": stage,
                "component": i + 1,
                "explained_variance_Xc": var_Xc[i] / total_var_X if total_var_X else np.nan,
                "explained_variance_Yc": var_Yc[i] / total_var_Y if total_var_Y else np.nan
            })
    except Exception as e:
        logger.error(f"Error processing {xc_file}: {e}")
        continue

# Save results
explained_var_df = pd.DataFrame(records)
explained_var_df.to_csv(OUTPUT_PATH, index=False)

logger.info(f"Explained variance results saved to {OUTPUT_PATH}")
