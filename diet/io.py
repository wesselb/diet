import yaml

from diet.quantity import Quantity, units

__all__ = ["load_file"]


def load_file(path):
    """Load recipe file.

    Args:
        path (str): Path to file.

    Returns:
        dict: Recipes by day.
        dict: Metadata.
    """
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    metadata = {}

    if "units" in data:
        for k in data["units"]:
            units[k] = Quantity.parse(data["units"][k])
        metadata["units"] = data["units"]
        del data["units"]

    return data, metadata
