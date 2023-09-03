import string
from numbers import Number

import numpy as np
from plum import dispatch

__all__ = ["units", "Quantity"]

units = {}
"""dict[str, :class:`Quantity`]: Simply a unit into a quantity with another unit."""

_numberlike = set(".0123456789")
"""set[str]: Characters that make up a number."""

_stringlike = set(string.ascii_letters)
"""set[str]: Characters that make up text, without numbers."""


class Quantity:
    """A quantity with a unit.

    Attributes:
        number (float): Number.
        unit (str): Unit.
    """

    @dispatch
    def __init__(self, number: Number, unit: str) -> None:
        """Construct an instance.

        Args:
            number (:class:`numbers.Number`): Number of quantity.
            unit (str): Unit of quantity.
        """
        if not unit:
            raise ValueError("Must specify a unit.")

        # Handle unicode in unit.
        unit = unit.replace("\u00B5", "u")
        if any(x not in _stringlike for x in unit):
            raise ValueError(f'Unicode in unit "{unit}" cannot fully be converted.')

        self.number = float(number)
        self.unit = unit

    def __repr__(self):
        return f"{self.number} {self.unit}"

    def simplify_unit(self) -> "Quantity":
        """Simplify the unit of the quantity according to :obj:`units`.

        Returns:
            :class:`Quantity`: Same quantity with simplified unit.
        """
        if self.unit in units:
            return (self.number * units[self.unit]).simplify_unit()
        else:
            return self

    @classmethod
    @dispatch
    def parse(cls, x: str, unit: str = "") -> "Quantity":
        """Parse a string and construct the corresponding quantity.

        Args:
            x (str or :class:`numbers.Number`): Specification of quantity.
            unit (str, optional): Unit.

        Returns:
            :class:`Quantity`: Specified quantity.
        """
        x = x.replace(" ", "")
        x = x.replace(",", ".")
        x = list(x)

        # Remove a possible prefix.
        while x and x[0] not in _numberlike:
            x.pop(0)

        # Parse the number.
        number = ""
        while x and x[0] in _numberlike:
            number += x.pop(0)
        if not number:
            number = np.nan
        else:
            number = float(number)

        # The remainder is the unit.
        parsed_unit = "".join(x)

        # Reconcile with a possible given unit.
        if unit and parsed_unit:
            if parsed_unit == unit:
                pass  # Everthing is OK.
            else:
                raise ValueError(
                    f'Parsed unit "{parsed_unit}" does not match given unit "{unit}".'
                )
        elif unit:
            pass  # Just use `unit`.
        elif parsed_unit:
            unit = parsed_unit

        return cls(number, unit)

    @classmethod
    @dispatch
    def parse(cls, x: Number, unit: str) -> "Quantity":
        return cls(x, unit)

    @dispatch
    def __eq__(self: "Quantity", other: "Quantity") -> bool:
        return self.number == other.number and self.unit == other.unit

    @dispatch
    def __add__(self: "Quantity", other: "Quantity") -> "Quantity":
        if self.unit != other.unit:
            raise RuntimeError(f"{self!r} does not have the same unit as {other!r}.")
        return Quantity(self.number + other.number, self.unit)

    @dispatch
    def __rmul__(self: "Quantity", other: Number) -> "Quantity":
        return Quantity(other * self.number, self.unit)

    @dispatch
    def __truediv__(self: "Quantity", other: Number) -> "Quantity":
        return Quantity(self.number / other, self.unit)

    @dispatch
    def __truediv__(self: "Quantity", other: "Quantity") -> float:
        if self.unit != other.unit:
            raise RuntimeError(f"{self!r} does not have the same unit as {other!r}.")
        return self.number / other.number
