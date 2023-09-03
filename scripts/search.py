import argparse

import wbml.out as out

from diet import find_ingredient

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="*")
    args = parser.parse_args()

    query = " ".join(args.query)
    out.kv("Data", find_ingredient(query))
