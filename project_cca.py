import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
#from scipy.linalg import subspace_angles
#from sklearn.decomposition import PCA
#from sklearn.decomposition import FastICA
from sklearn.cross_decomposition import CCA

import matplotlib.pyplot as plt

import mne

# Parameters
data_folder = "data"
eeg_channels = ['C3_M2', 'C4_M1', 'O1_M2', 'O2_M1']
eog_channels = ['LOC', 'ROC']
valid_stages = ['W', 'N1', 'N2', 'N3', 'R']
fmt = "%H:%M:%S"
#t0 = datetime.strptime("23:02:00", fmt)  # Reference start time

# Initialize results list
summary_results = []

# Iterate through files
file_pairs = [(f, f.replace(".edf", ".annot")) for f in os.listdir(data_folder) if f.endswith(".edf")]

for edf_file, annot_file in file_pairs:
    edf_path = os.path.join(data_folder, edf_file)
    #if not edf_path.endswith("apples-170368.edf"):
    #    continue
    annot_path = os.path.join(data_folder, annot_file)

    if not os.path.exists(annot_path):
        continue

    try:
        raw = mne.io.read_raw_edf(edf_path, preload=True, verbose=False)
        sfreq = int(raw.info['sfreq'])
        start_datetime = raw.info['meas_date'].replace(tzinfo=None)
        print(f"EDF {edf_path} Start:", start_datetime)

        #print(f"{edf_file}: total samples = {raw.n_times}, sfreq = {sfreq}")

        #channel_names = raw.ch_names
        #n_channels = len(channel_names)
        #print(f"Number of channels: {n_channels}")
        #print(f"Channels avail: {channel_names}")

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
            if stage in valid_stages:
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
                    print(f"Annotation parse error: {e}")


        print('epochs parsed: ', parsed_epochs[:5])
        stage_counts = Counter([stage for stage, _, _ in parsed_epochs])
        print(f'Stage count for subject {edf_file}: {stage_counts}')

        # Organize EEG and EOG segments
        eeg_data = {stage: [] for stage in valid_stages}
        eog_data = {stage: [] for stage in valid_stages}
        for s, start, stop in parsed_epochs:
            #if s == "R" and edf_path.endswith("apples-170368.edf"):
            #    print(f"Stage R interval: {start}–{stop} sec → samples {int(start * sfreq)}–{int(stop * sfreq)}")

            #start_sample = int(start * sfreq)
            #stop_sample = min(int(stop * sfreq), raw.n_times)
            start_sample = round(start * sfreq)
            stop_sample = min(round(stop * sfreq), raw.n_times)

            if start_sample < 0 or start_sample >= stop_sample:
                print(f"Invalid sample range for stage {s}: start={start_sample}, stop={stop_sample}, total={raw.n_times}")
                continue

            try:
                eeg = raw.get_data(picks=eeg_channels, start=start_sample, stop=stop_sample)
                eog = raw.get_data(picks=eog_channels, start=start_sample, stop=stop_sample)
                eeg_data[s].append(eeg)
                eog_data[s].append(eog)
            except Exception as e:
                print(f"Failed to extract data: stage={s}, start={start_sample}, stop={stop_sample}, error: {e}")
                continue

        # Define downsampling factor (e.g. 1 Hz)
        target_fs = 1
        factor = int(sfreq / target_fs)

        # Perform CCA
        for stage in valid_stages:
            if not eeg_data[stage] or not eog_data[stage]:
                print(f"Skipping stage {stage}: no data available.")
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
                    os.path.join(data_folder, f"{file_prefix}_Xc_downsampled.csv"), index=False
                )
                pd.DataFrame(Y_c_ds, columns=["Yc_1", "Yc_2"]).to_csv(
                    os.path.join(data_folder, f"{file_prefix}_Yc_downsampled.csv"), index=False
                )

                # Compute canonical correlation coefficients
                corr_coeffs = [np.corrcoef(X_c[:, i], Y_c[:, i])[0, 1] for i in range(X_c.shape[1])]
                
                # ---- Compute summary statistics ----
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
                print(f'Summary resulst for edf {edf_file} for stage {stage} written')

            except Exception as e:
                print(f"CCA failed for {edf_file}, stage {stage}: {e}")
    except Exception as e:
        print(f"Failed on {edf_file}: {e}")
    #    
        raw._data = None  # Detach memory-mapped data if present
        raw.annotations.delete(0, len(raw.annotations))  # Clear MNE annotations    
        del raw, eeg_data, eog_data
        import gc
        gc.collect()    

# Save results
results_df = pd.DataFrame(summary_results)
results_csv_path = os.path.join(data_folder, "eeg_eog_cca_summary_stats.csv")
results_df.to_csv(results_csv_path, index=False)

print('Results')
print(results_df)
