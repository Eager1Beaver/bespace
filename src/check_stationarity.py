import os
import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss

# Define the path to time-resolved CCA data
data_folder = "data/time_resolved_cca"

# List available CCA timeseries files
cca_files = [f for f in os.listdir(data_folder) if f.endswith("_cca_timeseries.csv")]

# Load a few representative files (max 3)
selected_files = cca_files[:]
results = []

for fname in selected_files:
    df = pd.read_csv(os.path.join(data_folder, fname))
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
output_path = os.path.join(data_folder, "stationarity_results.csv")
results_df.to_csv(output_path, index=False)
print(f"Stationarity results saved to {output_path}")
#print(results_df)
