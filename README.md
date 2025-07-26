## Investigating Brain–Eye Communication Subspaces During Sleep

### Overview
This project centers on exploring the low-dimensional communication subspace shared between EEG and EOG signals during different sleep stages (e.g., Wake, REM, N2). Specifically, we plan to:

- Segment the signals according to the provided sleep stage annotations;
- Perform dimensionality reduction (e.g., PCA) on EEG and EOG channels independently;
- Compute subspace angles between them to quantify alignment and shared structure;
- Compare how this alignment varies across sleep stages.

This approach will be adapted here for sleep-related brain–eye dynamics. The computation and data requirements are modest, and we plan to work with a small subset of EDFs (30 participants).

### Project Data
The raw data were obtained from the [National Sleep Research Resource](https://sleepdata.org/) database.

APPLES dataset from the National Sleep Research Resource

### Project Workflow

### Repository Structure

## References

## Instructions to run the project:
All command should run under project root/working-directory
```bash 
# clone the repository
git clone https://github.com/Eager1Beaver/schizo.git
cd schizo
# install Virtualenv is - a tool to set up your Python environments
pip install virtualenv
# create virtual environment (serve only this project):
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows
# activate virtual environment
venv\Scripts\activate # Windows
source venv/bin/activate # Linux
+ (venv) should appear as prefix to all command (run next command just after activating venv)
# update venv's python package-installer (pip) to its latest version
python.exe -m pip install --upgrade pip
# install projects packages (Everything needed to run the project)
pip install -e .
# install dev packages (Additional packages for linting, testing and other developer tools)
pip install -e .[dev]
# specify the project configuration: edit the config file and save the configuration
nano config.yaml
# run the main script
python main.py
``` 