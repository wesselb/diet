import wbml.out as out

__all__ = ["print_table"]


def print_table(data):
    """Print a table.

    Args:
        data (Iterable[tuple]): An iterable over rows, where every row is a tuple
            containing the values for all columns.
    """
    rows = [tuple(str(x) for x in row) for row in data]
    cols = list(zip(*rows))
    widths = [max(map(len, col)) for col in cols]
    table = ""
    for row in rows:
        for col, width in zip(row, widths):
            table += f"{{col:{width}s}} ".format(col=col)
        table += "\n"
    out.out(table)
