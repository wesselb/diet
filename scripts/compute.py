import argparse
from functools import reduce
from numbers import Number
from operator import add

import numpy as np
from plum import dispatch

from diet import Quantity, find_ingredient, load_file, nutrients, print_table, rdi


class Contents(dict):
    @dispatch
    def __rmul__(self, x: Number) -> "Contents":
        return Contents({k: x * v for k, v in self.items()})

    @dispatch
    def __truediv__(self, x: Number) -> "Contents":
        return Contents({k: v / x for k, v in self.items()})

    def __add__(self, other: "Contents") -> "Contents":
        result = Contents(self)
        for k in other.keys():
            try:
                result[k] += other[k]
            except KeyError:
                result[k] = other[k]
        return result


class Ingredients(list):
    pass


@dispatch
def find_weighted_ingredients(x: None, missing_is_zero: bool):
    return None


@dispatch
def find_weighted_ingredients(x: dict, missing_is_zero: bool):
    return {k: find_weighted_ingredients(v, missing_is_zero) for k, v in x.items()}


@dispatch
def find_weighted_ingredients(x: list, missing_is_zero: bool):
    return Ingredients(find_weighted_ingredients(xi, missing_is_zero) for xi in x)


@dispatch
def find_weighted_ingredients(x: str, missing_is_zero: bool):
    query, weight = x.split("|")
    weight = Quantity.parse(weight).simplify_unit()
    matched = find_ingredient(query)
    ratio = weight / matched["quantity"]
    contents = ratio * Contents(matched["contents"])
    if missing_is_zero:
        for v in contents.values():
            if np.isnan(v.number):
                v.number = 0
    return contents


@dispatch
def sum_ingredients(x: None):
    return Contents()


@dispatch
def sum_ingredients(x: dict):
    return reduce(add, map(sum_ingredients, x.values()))


@dispatch
def sum_ingredients(x: Ingredients):
    return reduce(add, x)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--ignore-missing", action="store_false")
    args = parser.parse_args()

    data, metadata = load_file(args.path)
    num_days = len(data)
    data = find_weighted_ingredients(data, not args.ignore_missing)
    data = sum_ingredients(data)
    data /= num_days  # Compute the daily average.

    # Print the result as a nice table.
    rows = []
    for k, v in data.items():
        if not np.isnan(v.number):
            if k in rdi:
                this_rdi = f"{v / rdi[k] * 100:.0f}%"
            else:
                this_rdi = ""
            rows.append((k, nutrients[k], f"{v.number:.1f} {v.unit}", this_rdi))
    print_table(rows)
