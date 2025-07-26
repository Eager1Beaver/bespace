import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
from sklearn.cross_decomposition import CCA

import mne

# Parameters
data_folder = "data"
output_folder = os.path.join(data_folder, "time_resolved_cca")
os.makedirs(output_folder, exist_ok=True)
eeg_channels = ['C3_M2', 'C4_M1', 'O1_M2', 'O2_M1']
eog_channels = ['LOC', 'ROC']
valid_stages = ['W', 'N1', 'N2', 'N3', 'R']
fmt = "%H:%M:%S"

win_len = 30  # seconds
step_len = 15  # seconds

file_pairs = [(f, f.replace(".edf", ".annot")) for f in os.listdir(data_folder) if f.endswith(".edf")]

for edf_file, annot_file in file_pairs:
    edf_path = os.path.join(data_folder, edf_file)
    annot_path = os.path.join(data_folder, annot_file)

    if not os.path.exists(annot_path):
        continue

    try:
        raw = mne.io.read_raw_edf(edf_path, preload=True, verbose=False)
        sfreq = int(raw.info['sfreq'])
        start_datetime = raw.info['meas_date'].replace(tzinfo=None)
        print(f"EDF {edf_path} Start:", start_datetime)

        # Read annotations
        with open(annot_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[1:]
        annotations = []
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

        stage_to_results = {stage: [] for stage in valid_stages}
        for stage, start, stop in parsed_epochs:
            t = start
            while t + win_len <= stop:
                start_sample = round(t * sfreq)
                stop_sample = round((t + win_len) * sfreq)

                if start_sample < 0 or stop_sample > raw.n_times:
                    t += step_len
                    continue

                try:
                    eeg = raw.get_data(picks=eeg_channels, start=start_sample, stop=stop_sample)
                    eog = raw.get_data(picks=eog_channels, start=start_sample, stop=stop_sample)
                    X = eeg.T
                    Y = eog.T

                    min_len = min(len(X), len(Y))
                    X = X[:min_len]
                    Y = Y[:min_len]

                    cca = CCA(n_components=2)
                    X_c, Y_c = cca.fit_transform(X, Y)
                    corr1 = np.corrcoef(X_c[:, 0], Y_c[:, 0])[0, 1]
                    corr2 = np.corrcoef(X_c[:, 1], Y_c[:, 1])[0, 1]

                    stage_to_results[stage].append({
                        "time_sec": t,
                        "cca_corr1": corr1,
                        "cca_corr2": corr2,
                        "subject": edf_file.replace(".edf", ""),
                        "stage": stage
                    })

                except Exception as e:
                    print(f"CCA failed in {edf_file} stage {stage} at t={t}: {e}")
                t += step_len

            for stage, results in stage_to_results.items():
                if results:
                    df_out = pd.DataFrame(results)
                    file_prefix = f"{edf_file.replace('.edf','')}_{stage}_cca_timeseries.csv"
                    df_out.to_csv(os.path.join(output_folder, file_prefix), index=False)
                    print(f"Saved CCA timeseries for {edf_file} stage {stage}")

    except Exception as e:
        print(f"Failed on {edf_file}: {e}")

    finally:
        raw._data = None
        del raw
        import gc
        gc.collect()
