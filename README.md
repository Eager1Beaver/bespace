# Investigating Brain–Eye Communication Subspaces During Sleep

## Project Overview

This project explores the coordination between brain and eye activity during different sleep stages using EEG and EOG signals. Canonical Correlation Analysis (CCA) is used to extract low-dimensional shared subspaces, offering insights into how EEG–EOG coupling varies across Wake, N1, N2, N3, and REM stages.

Key contributions:
- Time-resolved and static CCA analysis of EEG–EOG coupling.
- Entropy and trajectory analysis of canonical correlation dynamics.
- Visualizations summarizing sleep-stage specific brain–eye interactions.

The study uses the publicly available **APPLES dataset** from the [National Sleep Research Resource](https://sleepdata.org/datasets/apples).

---

## Repository Structure

```
.
├── main.py
├── src/
│   ├── config/config.yaml             # Project settings
│   ├── config_loader.py               # Reads config via OmegaConf
│   ├── logger.py                      # Logs status and errors
│   ├── project_cca.py                 # Static CCA by sleep stage
│   ├── time_resolved_cca_generator.py # Time-windowed CCA
│   ├── analyze_time_resolved_cca.py   # Entropy, stats, trajectories
│   ├── time_resolved_analysis_thematically_groupped.py  # Figures
│   ├── analyze_canonical_projections.py # Xc/Yc projection stats
│   ├── analyze_summary_stats.py       # Summary plots/stats
│   └── generate_figures_report.py     # Final figures for report
├── data/                              # EDFs, annotations, and output
├── report/figs/                       # Final PNG figures
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 📦 Installation

### Option 1: Using `requirements.txt`
```bash
git clone https://github.com/Eager1Beaver/bespace.git
cd bespace

python -m venv venv
source venv/bin/activate     # or venv\Scripts\activate on Windows

pip install -r requirements.txt
```

### Option 2: (optional) Using `pyproject.toml`
```bash
pip install .
```

---

## Configuration

All pipeline behavior is controlled from:
```
src/config/config.yaml
```

Edit the YAML file to enable or disable pipeline steps:
```yaml
run_params:
  run_static_cca: true
  run_time_resolved_cca: true
  run_static_analysis: true
  run_time_resolved_analysis: true
  generate_figures: true
```

You can also set:
- EEG and EOG channel names
- Input/output directories
- Window and step sizes for time-resolved CCA

---

## Usage

To run the full pipeline:
```bash
python main.py
```

Outputs will be saved to the paths defined in your config. This includes:
- Canonical correlation values
- Time-resolved trajectories and entropy stats
- Publication-ready visualizations

---

## Dataset

This project uses data from the **APPLES** study:
> The Apnea Positive Pressure Long-term Efficacy Study (APPLES) is a clinical trial available from NSRR.

You can access it here: https://sleepdata.org/datasets/apples

---

## References

- Canonical Correlation Analysis: https://scikit-learn.org/stable/modules/generated/sklearn.cross_decomposition.CCA.html
- MNE-Python Toolbox: https://mne.tools/stable/index.html
- NSRR (Sleep data): https://sleepdata.org/

---

## Acknowledgements

Developed as part of the "Data Science Applications in Neuroscience" course, using real EEG–EOG data to explore multimodal brain–body interactions during sleep.
