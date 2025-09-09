# Investigating Brain–Eye Communication Subspaces During Sleep

## Project Overview

This project quantifies how brain (EEG) and eye (EOG) activity co-vary across sleep stages by learning a **shared low-dimensional subspace** with Canonical Correlation Analysis (CCA). We use both **static (stage-wise)** and **time‑resolved (sliding‑window)** CCA to study the first two canonical correlations (ρ₁, ρ₂), their **temporal trajectories**, and the **distributional complexity** (entropy, skewness, kurtosis) of coupling. We further profile **explained variance** of the canonical variates to show that most cross‑modal structure lies in a compact subspace. Local **stationarity checks (ADF/KPSS)** support the use of fixed 30‑s windows for dynamics.

The study uses the publicly available **APPLES dataset** from the [National Sleep Research Resource](https://sleepdata.org/datasets/apples).

---

## Repository Structure

```
bespace/
│
├── .gitignore
├── main.py
├── pyproject.toml
├── README.md
├── requirements.txt
├── bespace.code-workspace
│
├── data/
│ ├── preproc_examples/ # CSV comparisons (before/after preprocessing)
│ ├── static_cca/ # Stage-wise summary stats + explained variance
│ ├── static_cca_analysis/ # Canonical projection stats + correlation summaries
│ ├── time_resolved_cca/ # Time-resolved outputs + stationarity results
│ └── time_resolved_cca_analysis/ # Aggregated trajectories, entropy, stagewise summaries
│
├── report/
│ ├── figs/ # Final figures (.png)
│ ├── report.tex # LaTeX source
│ ├── preamble.tex # LaTeX preamble
│ ├── report.bib # Bibliography
│ └── report.pdf # Compiled final report
│
└── src/
├── config/
│ └── config.yaml # Runtime settings and parameters
│
├── config_loader.py # Loads config via OmegaConf
├── logger.py # Logging configuration
│
├── preprocessing.py # Preprocessing functions (filtering, notch, etc.)
├── export_preproc_examples.py # Export before/after preprocessing CSVs
├── visualize_preproc_examples.py # Plot preprocessing examples
│
├── static_cca.py # Static CCA per stage
├── static_cca_analyze_summary_stats.py # Stats: boxplots, ANOVA
├── static_cca_analyze_canonical_projections.py # Projection KDEs and stats
├── static_cca_explained_variance.py # Explained variance computation
├── static_cca_visualize_explained_variance.py # Explained variance visualization
│
├── time_resolved_cca.py # Sliding-window CCA
├── time_resolved_cca_analysis.py # Stats, entropy, trajectories
├── time_resolved_cca_plotting_grouped.py # Visualization by stage/theme
├── time_resolved_cca_check_stationarity.py # ADF/KPSS stationarity checks
│
└── generate_figures_report.py # Final multi-panel figures

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

## ⚙️ Configuration

All pipeline behavior is controlled from:
```
src/config/config.yaml
```

Edit the YAML file to enable or disable pipeline steps:
```yaml
run_params:
  run_preproc_example: False
  run_static_cca: True
  run_time_resolved_cca: False
  run_static_analysis: False
  run_time_resolved_analysis: False
  generate_figures: False
```

You can also set:
- EEG/EOG channel names
- Input/output directories
- Preprocessing parameters (line noise, bandpass)
- Window and step sizes for time-resolved CCA

---

## Usage

To run the full pipeline:
```bash
python main.py
```

### What gets produced (by module)

**Static (stage-wise) CCA**
- `data/static_cca/eeg_eog_cca_summary_stats.csv` — per subject & stage summary of ρ₁, ρ₂ (used for Fig. 1).
- `data/static_cca/*_Xc_downsampled.csv`, `*_Yc_downsampled.csv` — 1 Hz canonical variates (for projection stats & KDEs).

**Time‑resolved CCA (30 s windows, 15 s step)**
- `data/time_resolved_cca/*_cca_timeseries.csv` — per stage timeseries of ρ₁, ρ₂ for each subject.
- `data/time_resolved_cca_analysis/stagewise_summary.csv` — mean/std/count of ρ₁, ρ₂ by stage.
- `data/time_resolved_cca_analysis/mean_cca_trajectory_by_stage.csv` — 10‑min binned trajectories by stage.
- `data/time_resolved_cca_analysis/entropy_by_subject_stage.csv` — entropy, mean, std, skew, kurt per subject-stage.
- `data/time_resolved_cca_analysis/subset_trajectories.csv` — a small sample for quick visualization.

**Explained Variance & Stationarity**
- `data/static_cca/explained_variance_by_stage.csv` — fraction of EEG/EOG variance captured by each CCA component.
- `data/time_resolved_cca_analysis/stationarity_results.csv` — ADF/KPSS pass/fail rates per window (if enabled).

**Figures**
- `report/figs/figure1_static_cca_boxplots.png` — static ρ₁/ρ₂ by stage.
- `report/figs/figure2_time_resolved_boxplots.png` — time‑resolved ρ₁/ρ₂ distributions by stage.
- `report/figs/figure3_cca_trajectories.png` — 10‑min mean trajectories by stage.
- `report/figs/figure4_entropy_boxplots.png` — entropy of ρ₁/ρ₂ by stage.

> Re‑generate all figures with:
> ```bash
> python src/generate_figures_report.py
> ```

---

## 📊 Interpreting Outputs (at a glance)

- **ρ₁, ρ₂**: Primary and secondary coupling strengths between EEG and EOG within a stage or window.
- **Trajectories (10‑min bins)**: Stage‑specific trends across the night (stable plateaus in N2/N3; broader variability in Wake/REM).
- **Entropy**: How concentrated vs. dispersed the coupling distribution is within a stage (lowest in N3; highest in Wake/REM).
- **Explained variance**: Confirms a compact, interpretable shared subspace (first two components capture a substantial fraction of variance).

See the full write‑up in `report/report.pdf` for details and statistics.

---

## Dataset

This project uses the **APPLES** study accessible via the National Sleep Research Resource (NSRR).
> The Apnea Positive Pressure Long-term Efficacy Study (APPLES) is a clinical trial available from NSRR.

- NSRR dataset portal: https://sleepdata.org/datasets/apples

Please ensure you have appropriate data-access credentials and follow the dataset’s terms of use.

---

## References (tools)

- Canonical Correlation Analysis (scikit‑learn): https://scikit-learn.org/stable/modules/generated/sklearn.cross_decomposition.CCA.html
- MNE-Python Toolbox: https://mne.tools/stable/index.html
- NSRR (Sleep data): https://sleepdata.org/

---

## Acknowledgements

Developed as part of the course **"Data Science Applications in Neuroscience"** to explore multimodal brain–eye coordination during sleep using real PSG recordings.
