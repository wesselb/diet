import numpy as np
import pytest
from plum import NotFoundLookupError

from diet.quantity import Quantity
from diet.quantity import units as _units


def test_construction_requires_unit():
    with pytest.raises(ValueError, match="(?i)must specify a unit"):
        Quantity(1, "")


def test_construction_handles_unicode():
    assert Quantity(1, "\u00B5g") == Quantity(1, "ug")
    with pytest.raises(ValueError, match="(?i)unicode (.*) cannot fully be converted"):
        Quantity(1, "\u221A")


def test_construction_converts_to_float():
    assert isinstance(Quantity(1, "g").number, float)


def test_repr():
    assert repr(Quantity(1, "g")) == "1.0 g"


@pytest.fixture()
def units():
    _old_units = dict(_units)
    _units.clear()
    yield _units
    _units.clear()
    for k, v in _old_units:
        _units[k] = v


def test_simplify_unit(units):
    units["egg"] = Quantity(100, "g")
    units["basket"] = Quantity(5, "egg")
    assert Quantity(2, "basket").simplify_unit() == Quantity(1000, "g")


def test_parse():
    assert Quantity.parse("per 100 g") == Quantity(100, "g")
    assert Quantity.parse("per 100 g", "g") == Quantity(100, "g")
    with pytest.raises(ValueError, match="(?i)does not match given unit"):
        Quantity.parse("per 100 g", "kg")

    assert Quantity.parse("50,5kg") == Quantity(50.5, "kg")
    assert Quantity.parse("50,5kg", "kg") == Quantity(50.5, "kg")
    with pytest.raises(ValueError, match="(?i)does not match given unit"):
        Quantity.parse("50,5kg", "g")

    assert Quantity.parse(5, "kg") == Quantity(5, "kg")

    # Check parsing an empty string.
    assert np.isnan(Quantity.parse("", "g").number)
    assert Quantity.parse("", "g").unit == "g"

    # Check parsing a string without given unit
    with pytest.raises(ValueError, match="(?i)must specify a unit"):
        Quantity.parse("")
    # A string without a number classifies as gibberish.
    with pytest.raises(ValueError, match="(?i)must specify a unit"):
        Quantity.parse("g")


def test_equality():
    assert Quantity(1, "g") == Quantity(1, "g")


def test_add():
    assert Quantity(1, "g") + Quantity(2, "g") == Quantity(3, "g")
    with pytest.raises(RuntimeError, match="(?i)does not have the same unit"):
        Quantity(1, "g") + Quantity(2, "kg")
    with pytest.raises(NotFoundLookupError):
        Quantity(1, "g") + 1


def test_mul():
    assert 5 * Quantity(3, "g") == Quantity(15, "g")
    with pytest.raises(TypeError):
        Quantity(5, "g") * Quantity(3, "g")


def test_div():
    assert Quantity(15, "g") / 3 == Quantity(5, "g")
    assert Quantity(15, "g") / Quantity(3, "g") == 5
    with pytest.raises(RuntimeError, match="(?i)does not have the same unit"):
        Quantity(15, "kg") / Quantity(3, "g")
