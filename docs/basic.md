# Basic Use

## Specification of Recipes

An example of a recipe file is as follows:

```
units:
  avo: 150 g
  egg: 100 g
  tomato: 75 g

Sat:
  dinner:
  - avocado | 2 avo
  - egg boiled | 4 egg
  - tomato raw | 2 tomato
  - sea salt | 0.25 g
```

You can add more days and more meals per day.

## Compute the Daily Average Nutrients

```bash
python scripts/compute.py recipes/test.txt
```

This sets all missing nutritional values to zero. If you want to instead only show the values which are know with certainty, run

```bash
python scripts/compute.py recipes/test.txt --ignore-missing
```

## Validate A Recipe File

```bash
python scripts/validate.py recipes/test.txt
```

## Show an Overview of All Nutrients

```bash
python scripts/nutrients_overview.py
```

## Search For an Ingredient

```bash
python scripts/search.py
```

To launch an interactive session, leave the argument empty:

```bash
python scripts/search.py avocado
```
