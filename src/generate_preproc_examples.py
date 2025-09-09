# generate_preproc_examples.py
from preprocessing import apply_preprocessing
from datetime import datetime, timedelta
from config_loader import load_config
from collections import defaultdict
from logger import logger
import pandas as pd
import mne, os

def _parse_time(tstr, TIME_FMTS):
    tstr = tstr.strip()
    for fmt in TIME_FMTS:
        try:
            return datetime.strptime(tstr, fmt).time()
        except Exception:
            continue
    raise ValueError(f"Unrecognized time format: {tstr!r}")

def _read_annotations(annot_path):
    """Return list of tuples: (stage, start_str, stop_str)."""
    out = []
    with open(annot_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    if not lines:
        return out
    
    for line in lines[1:]:
        parts = line.strip().split("\t")
        if len(parts) == 6:
            stage, _, _, start, stop, _ = parts
            out.append((stage.strip(), start.strip(), stop.strip()))
    return out

def _segments_seconds(annos, start_dt, SLEEP_STAGES, TIME_FMTS):
    segs = []
    for stage, start_str, stop_str in annos:
        if stage not in SLEEP_STAGES:
            continue
        try:
            start_clock = _parse_time(start_str, TIME_FMTS)
            stop_clock  = _parse_time(stop_str, TIME_FMTS)

            sdt = datetime.combine(start_dt.date(), start_clock)
            edt = datetime.combine(start_dt.date(), stop_clock)

            # Handle midnight crossing
            if edt < sdt:
                edt += timedelta(days=1)

            # Handle recording start crossing
            if sdt < start_dt:
                sdt += timedelta(days=1)
                edt += timedelta(days=1)

            s_sec = (sdt - start_dt).total_seconds()
            e_sec = (edt - start_dt).total_seconds()

            if e_sec > s_sec:
                segs.append((stage, s_sec, e_sec))
        except Exception as e:
            logger.error(f"Annotation parse error for stage={stage} ({start_str}-{stop_str}): {e}")
    return segs

def _pick_window(segs, win_len, preferred_order):
    """
    Pick the first stage (by preferred_order) that has any segment >= WINDOW_LENGTH.
    Return (stage, start_sec, stop_sec) for a middle window of length WINDOW_LENGTH.
    """
    # aggregate by stage for logging and selection
    by_stage = defaultdict(list)
    for stg, s, e in segs:
        by_stage[stg].append((s, e))

    # Log available durations per stage
    for stg, lst in by_stage.items():
        total = sum(e - s for s, e in lst)
        longest = max((e - s) for s, e in lst)
        logger.info(f"Stage {stg}: total_dur={total:.1f}s, longest={longest:.1f}s, n_segments={len(lst)}")

    for stg in preferred_order:
        if stg not in by_stage:
            continue
        # find first long-enough segment
        for s, e in sorted(by_stage[stg], key=lambda x: (x[1] - x[0]), reverse=True):
            if (e - s) >= win_len:
                mid = (s + e) / 2.0
                start = max(s, mid - win_len / 2.0)
                stop  = start + win_len
                return stg, start, stop

    return None  # none found

def main():

    # Parameters
    config = load_config()
    WINDOW_LENGTH = config.time_cca_params.window_length # 30 seconds
    SLEEP_STAGES = config.data.sleep_stages # ['W', 'N1', 'N2', 'N3', 'R']
    TIME_FMTS = ["%H:%M:%S", "%H:%M:%S.%f"] # handle HH:MM:SS and HH:MM:SS.mmm
    DATA_FOLDER = config.data.data_dir # "data/apples"
    OUTPUT_FOLDER  = config.preprocess.output_dir # "data/apples/preproc_examples"
    EEG_CHANNELS = config.data.eeg_channels # ['C3_M2', 'C4_M1', 'O1_M2', 'O2_M1']
    EOG_CHANNELS = config.data.eog_channels # ['LOC', 'ROC']
    SLEEP_STAGES = config.data.sleep_stages # ['W', 'N1', 'N2', 'N3', 'R']

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # Choose first available EDF
    edfs = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".edf")]
    if not edfs:
        logger.error("No EDF files in DATA_FOLDER.")
        return
    edf = edfs[0]
    annot = edf.replace(".edf", ".annot")
    edf_path = os.path.join(DATA_FOLDER, edf)
    annot_path = os.path.join(DATA_FOLDER, annot)

    if not os.path.exists(annot_path):
        logger.error(f"Missing annot for {edf}")
        return

    # Load EDF
    raw = mne.io.read_raw_edf(edf_path, preload=True, verbose=False)
    start_dt = raw.info.get('meas_date')
    if isinstance(start_dt, (list, tuple)):
        start_dt = start_dt[0]
    if start_dt is None:
        logger.warning("meas_date is None; assuming 1970-01-01.")
        start_dt = datetime(1970,1,1)
    else:
        start_dt = start_dt.replace(tzinfo=None)

    # Parse annotations
    annos = _read_annotations(annot_path)
    segs = _segments_seconds(annos, start_dt, SLEEP_STAGES, TIME_FMTS)

    if not segs:
        logger.error("No valid segments from annotations.")
        return

    # Pick window with preferred order
    chosen = _pick_window(segs, WINDOW_LENGTH, SLEEP_STAGES)
    if chosen is None:
        logger.error(f"No segment >= {WINDOW_LENGTH}s found in any of {SLEEP_STAGES}. "
                     f"Consider reducing WINDOW_LENGTH or checking annotations.")
        return

    stage, s_sec, e_sec = chosen
    sf = raw.info['sfreq']
    s_samp = int(round(s_sec * sf))
    e_samp = int(round(e_sec * sf))

    try:
        # Optional preprocessing (EEG/EOG only)
        raw_proc = apply_preprocessing(raw, EEG_CHANNELS, EOG_CHANNELS, config)
    except Exception as e:
        logger.error(f"Failed to preprocess data for subject {edf_path} , error: {e}")

    # Export per-channel CSVs: time_s, raw_uV, preproc_uV
    picks = EEG_CHANNELS + EOG_CHANNELS
    times = raw.times[s_samp:e_samp]

    for ch in picks:
        raw_v = raw.get_data(picks=[ch], start=s_samp, stop=e_samp).ravel() * 1e6 # µV
        pre_v = raw_proc.get_data(picks=[ch], start=s_samp, stop=e_samp).ravel() * 1e6

        df = pd.DataFrame({"time_s": times, "raw_uV": raw_v, "preproc_uV": pre_v})
        safe_ch = ch.replace("/", "-")
        out_csv = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(edf)[0]}_{stage}_{safe_ch}_{WINDOW_LENGTH}s.csv")
        df.to_csv(out_csv, index=False)

    logger.info(f"Saved before/after CSVs to {OUTPUT_FOLDER} for stage {stage}.")

if __name__ == "__main__":
    main()
