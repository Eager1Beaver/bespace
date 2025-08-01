import yaml
import subprocess
import os
from src.logger import logger

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
    # Load config file
    config_path = "src/config/config.yaml"
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        return

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Step-by-step execution based on config flags
    if config.get("run_static_cca", False):
        run_script("project_cca.py")

    if config.get("run_time_resolved_cca", False):
        run_script("time_resolved_cca_generator.py")

    if config.get("run_static_analysis", False):
        run_script("analyze_canonical_projections.py")
        run_script("analyze_summary_stats.py")

    if config.get("run_time_resolved_analysis", False):
        run_script("analyze_time_resolved_cca.py")
        run_script("time_resolved_analysis_thematically_groupped.py")    

    if config.get("generate_figures", False):
        run_script("generate_figures_report.py")

    logger.info("Pipeline completed.")

if __name__ == "__main__":
    main()
