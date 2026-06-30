import os
import yaml

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(_PROJECT_ROOT, "config", "sources.yaml")


def load_sources():
    with open(CONFIG_FILE, "r") as file:
        return yaml.safe_load(file)["sources"]


def get_source(source_name: str):
    sources = load_sources()

    if source_name not in sources:
        raise ValueError(f"{source_name} not found in sources.yaml")

    source = sources[source_name]

    if not source.get("enabled", False):
        raise ValueError(f"{source_name} is disabled")

    return source


def get_enabled_sources():
    return {
        name: source
        for name, source in load_sources().items()
        if source.get("enabled", False)
    }