import subprocess
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import yaml
from plum import dispatch

from diet.quantity import Quantity

__all__ = ["find_ingredient", "nutrients", "rdi"]

_data_root = Path(__file__).parents[1] / "data"

ingredients = pd.read_csv(_data_root / "nevo2021" / "data.csv", na_filter=False)
""":class:`pd.DataFrame`: All ingredient data."""

ingredients_search_cols = [
    "Voedingsmiddelnaam/Dutch food name",
    "Engelse naam/Food name",
    "Synoniem",
]
"""list[str]: Columns that should be used to search for ingredients."""

ingredients_data_cols = ingredients.columns[11:]
"""list[str]: Columns that contain nutritional information."""

ingredients_search_list = []
"""list[str]: List of all ingredients."""
for c in ingredients_search_cols:
    ingredients_search_list.extend(ingredients[c])
ingredient_search_list = list(sorted(np.unique(ingredients_search_list)))


@dispatch
def find_ingredient(query: Optional[str]):
    """Find an ingredient.

    Args:
        query (str, optional): Query. Do not specify to launch an interactive search.

    Returns:
        dict: Ingredient information.
    """
    command = ["fzf", "-i"]
    if query:
        command += ["--filter", query]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = p.communicate("\n".join(ingredient_search_list).encode())

    # Find the best `fzf` match.
    matches = stdout.decode().split("\n")
    if matches:
        fzf_match = matches[0]
    else:
        raise RuntimeError(f'No match for query "{query}".')

    # Find the corresponding row from the data frame.
    row = None
    for c in ingredients_search_cols:
        mask = ingredients[c] == fzf_match
        if any(mask):
            row = ingredients[mask].iloc[0]
            break
    assert row is not None, "Could not match `fzf` result."

    # Assemble result.
    contents = {}
    for c in ingredients_data_cols:
        col_name, unit = c.rsplit(" ")
        unit = unit[1:-1]  # Remove parenthesis.
        contents[col_name] = Quantity.parse(row[c], unit)
    return {
        "name": {
            "dutch": row["Voedingsmiddelnaam/Dutch food name"],
            "english": row["Engelse naam/Food name"],
        },
        "quantity": Quantity.parse(row["Hoeveelheid/Quantity"]),
        "contents": contents,
    }


@dispatch
def find_ingredient():
    return find_ingredient(None)


_nutrients_data = pd.read_csv(
    _data_root / "nevo2021" / "nutrients.csv", na_filter=False
)
nutrients = {}
"""dict[str, str]: Map nutrient abbreviations to descriptive names."""
for _, row in _nutrients_data.iterrows():
    nutrients[row["Nutrient-code"]] = row["Component"].strip()

with open(_data_root / "rdi.yaml", "r") as f:
    _data_rdi = yaml.safe_load(f)
rdi = {k: Quantity.parse(v) for k, v in _data_rdi.items()}
"""dict[str, :class:`diet.quantity.Quantity`]: RDIs per nutrient."""
