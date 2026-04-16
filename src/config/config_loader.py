import yaml
import os


def load_config():
    """
    Loads config.yaml from src/config/
    """

    current_dir = os.path.dirname(__file__)
    config_path = os.path.join(current_dir, "config.yaml")

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config