import os
import yaml


def read_config(project_dir):
    config_file = os.path.join(project_dir, '.marteau.yml')
    with open(config_file) as f:
        return yaml.load(f.read())
