# time_resolved_cca_check_stationarity.py
from statsmodels.tsa.stattools import adfuller, kpss
from config_loader import load_config
from logger import logger
import pandas as pd
import os

# Parameters
config = load_config()

DATA_FOLDER = config.time_cca_params.output_dir  # "data/time_resolved_cca"
OUTPUT_PATH = os.path.join(DATA_FOLDER, "stationarity_results.csv")

# List CCA timeseries files
cca_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith("_cca_timeseries.csv")]

results = []

for fname in cca_files:
    df = pd.read_csv(os.path.join(DATA_FOLDER, fname))
    subject = fname.replace("_cca_timeseries.csv", "")

    for comp in ["cca_corr1", "cca_corr2"]:
        values = df[comp].dropna().values

        if len(values) < 10:
            continue  # too few values to test

        # ADF Test
        adf_stat, adf_pval, _, _, _, _ = adfuller(values)

        # KPSS Test
        try:
            kpss_stat, kpss_pval, _, _ = kpss(values, regression='c')
        except:
            kpss_stat, kpss_pval = None, None

        results.append({
            "subject": subject,
            "component": comp,
            "adf_pval": adf_pval,
            "adf_stationary": adf_pval < 0.05,
            "kpss_pval": kpss_pval,
            "kpss_stationary": kpss_pval is not None and kpss_pval > 0.05
        })

results_df = pd.DataFrame(results)

# Save results to CSV
results_df.to_csv(OUTPUT_PATH, index=False)
logger.info(f"Stationarity results saved to {OUTPUT_PATH}")
