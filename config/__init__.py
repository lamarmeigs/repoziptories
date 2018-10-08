import os

import yaml


def _get_config(file_path):
    """Read the configuration from the given YAML file, overriding individual
    values from environment variables.

    Args:
        file_path (str): absolute or relative path to the YAML file to parse

    Return:
        dict
    """
    with open(file_path) as config_file:
        config = yaml.load(config_file)
    for key, value in config.items():
        config[key] = os.getenv(key.upper(), value)
    return config


config = _get_config('config/config.yaml')
