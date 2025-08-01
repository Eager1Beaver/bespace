# config_loader.py
from omegaconf import OmegaConf
import os

def load_config(config_path="config/config.yaml"):
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    return OmegaConf.load(config_path)
