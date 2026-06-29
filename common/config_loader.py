import yaml

CONFIG_FILE = "config/sources.yml"


def load_sources():
    with open(CONFIG_FILE, "r") as file:
        return yaml.safe_load(file)["sources"]


def get_source(source_name: str):
    sources = load_sources()

    if source_name not in sources:
        raise ValueError(f"{source_name} not found in sources.yml")

    source = sources[source_name]

    if not source.get("enabled", False):
        raise ValueError(f"{source_name} is disabled")

    return source