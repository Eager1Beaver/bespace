# static_cca.py
from sklearn.cross_decomposition import CCA
from datetime import datetime, timedelta
from config_loader import load_config
from collections import Counter
from logger import logger
import pandas as pd
import numpy as np
import mne
import os
import gc

# Parameters
config = load_config()

DATA_FOLDER = config.data.data_dir # "data/apples"
OUTPUT_FOLDER = config.static_cca_params.output_dir # "data/static_cca"
EEG_CHANNELS = config.data.eeg_channels # ['C3_M2', 'C4_M1', 'O1_M2', 'O2_M1']
EOG_CHANNELS = config.data.eog_channels # ['LOC', 'ROC']
SLEEP_STAGES = config.data.sleep_stages # ['W', 'N1', 'N2', 'N3', 'R']
DOWNSAMPLING_FACTOR = config.static_cca_params.downsampling_factor # 1
fmt = "%H:%M:%S"

# Initialize results list
summary_results = []

# Iterate through .edf/.annot files
file_pairs = [(f, f.replace(".edf", ".annot")) for f in os.listdir(DATA_FOLDER) if f.endswith(".edf")]

for edf_file, annot_file in file_pairs:
    edf_path = os.path.join(DATA_FOLDER, edf_file)
    annot_path = os.path.join(DATA_FOLDER, annot_file)

    if not os.path.exists(annot_path):
        continue

    try:
        raw = mne.io.read_raw_edf(edf_path, preload=True, verbose=False)
        sfreq = int(raw.info['sfreq'])
        start_datetime = raw.info['meas_date'].replace(tzinfo=None)
        logger.info(f"EDF {edf_path} Start:", start_datetime)

        # Read annotations
        with open(annot_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[1:]
        annotations = []
        starts = []
        for line in lines:
            parts = line.strip().split("\t")
            if len(parts) == 6:
                stage, _, _, start, stop, _ = parts
                annotations.append((stage, start, stop))

        parsed_epochs = []
        for stage, start_str, stop_str in annotations:
            if stage in SLEEP_STAGES:
                try:
                    start_clock = datetime.strptime(start_str, fmt).time()
                    stop_clock = datetime.strptime(stop_str, fmt).time()

                    start_time = datetime.combine(start_datetime.date(), start_clock)
                    stop_time = datetime.combine(start_datetime.date(), stop_clock)

                    # Handle midnight crossing
                    if stop_time < start_time:
                        stop_time += timedelta(days=1)
                    if start_time < start_datetime:
                        start_time += timedelta(days=1)
                        stop_time += timedelta(days=1)

                    start_sec = (start_time - start_datetime).total_seconds()
                    stop_sec = (stop_time - start_datetime).total_seconds()

                    parsed_epochs.append((stage, start_sec, stop_sec))
                except Exception as e:
                    logger.error(f"Annotation parse error: {e}")


        logger.info('Epochs parsed: ', parsed_epochs[:5])
        stage_counts = Counter([stage for stage, _, _ in parsed_epochs])
        logger.info(f'Stage count for subject {edf_file}: {stage_counts}')

        # Organize EEG and EOG segments
        eeg_data = {stage: [] for stage in SLEEP_STAGES}
        eog_data = {stage: [] for stage in SLEEP_STAGES}
        for s, start, stop in parsed_epochs:
            start_sample = round(start * sfreq)
            stop_sample = min(round(stop * sfreq), raw.n_times)

            if start_sample < 0 or start_sample >= stop_sample:
                logger.warning(f"Invalid sample range for stage {s}: start={start_sample}, stop={stop_sample}, total={raw.n_times}")
                continue

            try:
                eeg = raw.get_data(picks=EEG_CHANNELS, start=start_sample, stop=stop_sample)
                eog = raw.get_data(picks=EOG_CHANNELS, start=start_sample, stop=stop_sample)
                eeg_data[s].append(eeg)
                eog_data[s].append(eog)
            except Exception as e:
                logger.error(f"Failed to extract data: stage={s}, start={start_sample}, stop={stop_sample}, error: {e}")
                continue

        # Set a downsampling factor
        target_fs = DOWNSAMPLING_FACTOR
        factor = int(sfreq / target_fs)

        # Perform CCA
        for stage in SLEEP_STAGES:
            if not eeg_data[stage] or not eog_data[stage]:
                logger.info(f"Skipping stage {stage}: no data available.")
                continue
            eeg_agg = np.hstack(eeg_data[stage])
            eog_agg = np.hstack(eog_data[stage])

            try:
                # Transpose to (n_samples, n_features)
                X = eeg_agg.T
                Y = eog_agg.T

                # Ensure same number of samples
                min_len = min(len(X), len(Y))
                X = X[:min_len]
                Y = Y[:min_len]

                cca = CCA(n_components=2)
                X_c, Y_c = cca.fit_transform(X, Y)

                # ---- Save downsampled canonical projections ----
                if len(X_c) > factor:
                    X_c_ds = X_c[::factor, :]
                    Y_c_ds = Y_c[::factor, :]
                else:
                    X_c_ds = X_c
                    Y_c_ds = Y_c

                file_prefix = f"{edf_file.replace('.edf','')}_{stage}"

                # Save downsampled projections
                pd.DataFrame(X_c_ds, columns=["Xc_1", "Xc_2"]).to_csv(
                    os.path.join(OUTPUT_FOLDER, f"{file_prefix}_Xc_downsampled.csv"), index=False
                )
                pd.DataFrame(Y_c_ds, columns=["Yc_1", "Yc_2"]).to_csv(
                    os.path.join(OUTPUT_FOLDER, f"{file_prefix}_Yc_downsampled.csv"), index=False
                )

                # Compute canonical correlation coefficients
                corr_coeffs = [np.corrcoef(X_c[:, i], Y_c[:, i])[0, 1] for i in range(X_c.shape[1])]
                
                # Compute summary statistics
                summary = {
                    "subject": edf_file,
                    "stage": stage,
                    "cca_corr1": corr_coeffs[0],
                    "cca_corr2": corr_coeffs[1] if len(corr_coeffs) > 1 else np.nan
                }

                for idx in range(X_c.shape[1]):
                    x_vals = X_c[:, idx]
                    summary[f"Xc{idx+1}_mean"] = np.mean(x_vals)
                    summary[f"Xc{idx+1}_std"] = np.std(x_vals)
                    summary[f"Xc{idx+1}_25p"] = np.percentile(x_vals, 25)
                    summary[f"Xc{idx+1}_median"] = np.median(x_vals)
                    summary[f"Xc{idx+1}_75p"] = np.percentile(x_vals, 75)

                for idx in range(Y_c.shape[1]):
                    y_vals = Y_c[:, idx]
                    summary[f"Yc{idx+1}_mean"] = np.mean(y_vals)
                    summary[f"Yc{idx+1}_std"] = np.std(y_vals)
                    summary[f"Yc{idx+1}_25p"] = np.percentile(y_vals, 25)
                    summary[f"Yc{idx+1}_median"] = np.median(y_vals)
                    summary[f"Yc{idx+1}_75p"] = np.percentile(y_vals, 75)

                summary_results.append(summary)
                logger.info(f'Summary resulst for edf {edf_file} for stage {stage} written')

            except Exception as e:
                logger.error(f"CCA failed for {edf_file}, stage {stage}: {e}")
    except Exception as e:
        logger.error(f"Failed on {edf_file}: {e}")
    #
        raw._data = None  # Detach memory-mapped data if present
        raw.annotations.delete(0, len(raw.annotations))  # Clear MNE annotations    
        del raw, eeg_data, eog_data
        gc.collect() # Clean up memory

# Save results
results_df = pd.DataFrame(summary_results)
results_csv_path = os.path.join(OUTPUT_FOLDER, "eeg_eog_cca_summary_stats.csv")
results_df.to_csv(results_csv_path, index=False)

logger.info(f'The summary statistics saved to {results_csv_path}')
