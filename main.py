# main.py
import subprocess
import os

from src.logger import logger
from src.config_loader import load_config

# Helper to run a Python script
def run_script(script_name):
    script_path = os.path.join(os.getcwd(), "src", script_name)
    if not os.path.isfile(script_path):
        logger.error(f"Script not found: {script_path}")
        return
    try:
        logger.info(f"Running: {script_path}")
        subprocess.run(["python", script_path], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Script {script_name} failed with error: {e}")


def main():
    # Load config
    config = load_config()

    # Step-by-step execution based on flags in run_params
    run_flags = config.run_params

    if run_flags.run_preproc_example:
        run_script("generate_preproc_examples.py")
        run_script("visualize_preproc_examples.py")

    if run_flags.run_static_cca:
        run_script("static_cca.py")

    if run_flags.run_static_analysis:
        run_script("static_cca_analyze_canonical_projections.py")
        run_script("stataic_cca_analyze_summary_stats.py")
        run_script("static_cca_explained_variance.py") 

    if run_flags.run_time_resolved_cca:
        run_script("time_resolved_cca.py")

    if run_flags.run_time_resolved_analysis:
        run_script("time_resolved_cca_analysis.py")
        run_script("time_resolved_cca_check_stationarity.py")

    if run_flags.generate_figures:
        run_script("generate_figures_report.py")
        run_script("static_cca_visualize_explained_variance.py")
        run_script("time_resolved_cca_plotting_groupped.py")

    logger.info("Pipeline completed.")

if __name__ == "__main__":
    main()
