# preprocessing.py
import mne

def _notch_filter(raw, picks, line_hz, harmonics=True):
    if picks is None or (hasattr(picks, "__len__") and len(picks) == 0):
        return

    try:
        lh = float(line_hz) if line_hz is not None else None
    except Exception:
        lh = None
    if lh is None or lh <= 0:
        return

    freqs = [lh]
    if harmonics:
        sfreq = float(raw.info["sfreq"])
        for k in (2, 3):
            f = lh * k
            if f < sfreq / 2.0:
                freqs.append(f)

    raw.notch_filter(freqs=freqs, picks=picks, method="spectrum_fit", verbose=False)

def _to_list(x):
    try:
        return list(x)
    except Exception:
        return [x]

def _filter_existing(raw, names):
    present = [ch for ch in names if ch in raw.ch_names]
    missing = [ch for ch in names if ch not in raw.ch_names]
    return present, missing

def apply_preprocessing(raw_in, eeg_chs, eog_chs, cfg):
    if not getattr(cfg.preprocess, "enabled", False):
        return raw_in

    raw = raw_in.copy()

    eeg_chs = _to_list(eeg_chs)
    eog_chs = _to_list(eog_chs)

    eeg_chs, eeg_missing = _filter_existing(raw, eeg_chs)
    eog_chs, eog_missing = _filter_existing(raw, eog_chs)
    if eeg_missing or eog_missing:
        import warnings
        warnings.warn(f"Preproc: missing channels ignored. EEG missing={eeg_missing}, EOG missing={eog_missing}")

    eeg_picks = mne.pick_channels(raw.ch_names, include=eeg_chs)
    eog_picks = mne.pick_channels(raw.ch_names, include=eog_chs)

    line_hz = getattr(cfg.preprocess, "line_hz", None)
    _notch_filter(raw, eeg_picks, line_hz, harmonics=True)
    _notch_filter(raw, eog_picks, line_hz, harmonics=True)

    eeg_hp = float(cfg.preprocess.eeg.hp); eeg_lp = float(cfg.preprocess.eeg.lp)
    eog_hp = float(cfg.preprocess.eog.hp); eog_lp = float(cfg.preprocess.eog.lp)

    if len(eeg_picks) > 0:
        raw.filter(l_freq=eeg_hp, h_freq=eeg_lp, picks=eeg_picks,
                   phase='zero', fir_design='firwin', verbose=False)
    if len(eog_picks) > 0:
        raw.filter(l_freq=eog_hp, h_freq=eog_lp, picks=eog_picks,
                   phase='zero', fir_design='firwin', verbose=False)

    return raw
