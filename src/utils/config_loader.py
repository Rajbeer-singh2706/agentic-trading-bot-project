import yaml
from pathlib import Path


def load_config(config_path: str | None = None) -> dict:
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent / "config" / "config.yaml"

    print(config_path)
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config 


if __name__ == '__main__':
    print(load_config())
    print("name")

#python src/utils/config_loader.py
