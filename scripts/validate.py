import argparse

import getch
import wbml.out as out
import yaml
from plum import dispatch

from diet import find_ingredient, load_file


@dispatch
def validate(x: dict):
    for k, v in x.items():
        with out.Section(k):
            validate(v)


@dispatch
def validate(x: list):
    for i, xi in enumerate(x):
        out.out(xi)
        query, quantity = xi.split("|")

        # Print the current match.
        matched = find_ingredient(query)
        dutch = matched["name"]["dutch"]
        english = matched["name"]["english"]
        out.out(f'Matched "{dutch}"/"{english}". Is this validate? [y/n]')

        # Ask whether the current match is right. If it isn't, correct it.
        while True:
            response = getch.getch()
            if response not in {"y", "n"}:
                out.out('Invalid response. Please reply "y" or "n".')
            else:
                if response == "y":
                    out.out("OK!")
                else:
                    fixed = find_ingredient()
                    with out.Section("Fixed"):
                        x[i] = fixed["name"]["dutch"] + " |" + quantity
                        out.out(x[i])
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate and validate all ingredients in a recipe."
    )
    parser.add_argument("path")
    args = parser.parse_args()

    data, metadata = load_file(args.path)
    validate(data)
    # Write validateed file.
    with open(args.path, "w") as f:
        yaml.dump(metadata, f, sort_keys=False)
        yaml.dump(data, f, sort_keys=False)
