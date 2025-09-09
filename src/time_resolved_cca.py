# time_resolved_cca.py
from preprocessing import apply_preprocessing
from sklearn.cross_decomposition import CCA
from datetime import datetime, timedelta
from config_loader import load_config
from logger import logger
import pandas as pd
import numpy as np
import mne
import os
import gc

# Parameters
config = load_config()

DATA_FOLDER = config.data.data_dir # "data/apples"
OUTPUT_FOLDER = config.time_cca_params.output_dir # "data/time_resolved_cca"
EEG_CHANNELS = config.data.eeg_channels # ['C3_M2', 'C4_M1', 'O1_M2', 'O2_M1']
EOG_CHANNELS = config.data.eog_channels # ['LOC', 'ROC']
SLEEP_STAGES = config.data.sleep_stages # ['W', 'N1', 'N2', 'N3', 'R']
WINDOW_LENGTH = config.time_cca_params.window_length # 30 seconds
STEP_LENGTH = config.time_cca_params.step_length # 15 seconds
fmt = "%H:%M:%S"

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

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

        try:
            # Optional preprocessing (EEG/EOG only)
            raw_proc = apply_preprocessing(raw, EEG_CHANNELS, EOG_CHANNELS, config)
        except Exception as e:
            logger.error(f"Failed to preprocess data for subject {edf_file} , error: {e}")

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

        # Perform time-resolved CCA
        stage_to_results = {stage: [] for stage in SLEEP_STAGES}
        for stage, start, stop in parsed_epochs:
            t = start
            while t + WINDOW_LENGTH <= stop:
                start_sample = round(t * sfreq)
                stop_sample = round((t + WINDOW_LENGTH) * sfreq)

                if start_sample < 0 or stop_sample > raw.n_times:
                    t += STEP_LENGTH
                    continue    

                try:
                    eeg = raw_proc.get_data(picks=EEG_CHANNELS, start=start_sample, stop=stop_sample)
                    eog = raw_proc.get_data(picks=EOG_CHANNELS, start=start_sample, stop=stop_sample)
                    X = eeg.T
                    Y = eog.T

                    min_len = min(len(X), len(Y))
                    X = X[:min_len]
                    Y = Y[:min_len]

                    cca = CCA(n_components=2)
                    X_c, Y_c = cca.fit_transform(X, Y)

                    # Compute canonical correlation coefficients
                    corr1 = np.corrcoef(X_c[:, 0], Y_c[:, 0])[0, 1]
                    corr2 = np.corrcoef(X_c[:, 1], Y_c[:, 1])[0, 1]

                    # Compute summary statistics
                    stage_to_results[stage].append({
                        "time_sec": t,
                        "cca_corr1": corr1,
                        "cca_corr2": corr2,
                        "subject": edf_file.replace(".edf", ""),
                        "stage": stage
                    })

                except Exception as e:
                    logger.error(f"CCA failed in {edf_file} stage {stage} at t={t}: {e}")
                t += STEP_LENGTH

            # Save results
            for stage, results in stage_to_results.items():
                if results:
                    df_out = pd.DataFrame(results)
                    file_prefix = f"{edf_file.replace('.edf','')}_{stage}_cca_timeseries.csv"
                    df_out.to_csv(os.path.join(OUTPUT_FOLDER, file_prefix), index=False)
                    logger.info(f"Saved CCA timeseries for {edf_file} stage {stage}")

    except Exception as e:
        logger.error(f"Failed on {edf_file}: {e}")

    finally:
        raw_proc._data = None  # Detach memory-mapped data if present
        raw_proc.set_annotations(None)  # Clear MNE annotations    
        del raw_proc
        gc.collect() # Clean up memory
