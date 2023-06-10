#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


import pytest

from vhatable.filters import PartialOr
from vhatable.filters import Equal
from vhatable.filters import Equals
from vhatable.filters import PartialMultipleAnd
from vhatable.filters import PartialDate


def test_partial_or_false():
    """TODO"""
    filterr = PartialOr("name", ["value2", "value3"], True)
    row = {"name": "value1"}
    assert not filterr(row)


def test_partial_or_true0():
    """TODO"""
    filterr = PartialOr("name", [], True)
    row = {"name": "value2"}
    assert filterr(row)


def test_partial_or_true1():
    """TODO"""
    filterr = PartialOr("name", ["value2", "value3"], True)
    row = {"name": "value2"}
    assert filterr(row)


def test_partial_or_true2():
    """TODO"""
    filterr = PartialOr("name", ["val", "ue3"], True)
    row = {"name": "value2"}
    assert filterr(row)


def test_partial_or_true3():
    """TODO"""
    filterr = PartialOr("name", ["kal", "iuu3"], True)
    row = {"name": "value2"}
    assert not filterr(row)


def test_equal_true0():
    """TODO"""
    filterr = Equal("name", None)
    row = {"name": "value"}
    assert filterr(row)


def test_equal_true():
    """TODO"""
    filterr = Equal("name", "value")
    row = {"name": "value"}
    assert filterr(row)


def test_equal_false1():
    """TODO"""
    filterr = Equal("name", "val")
    row = {"name": "value"}
    assert not filterr(row)


def test_equal_false2():
    """TODO"""
    filterr = Equal("name", "value")
    row = {"name": "value2"}
    assert not filterr(row)


def test_equals_true0():
    """TODO"""
    filterr = Equals("name", [])
    row = {"name": "value2"}
    assert filterr(row)


@pytest.mark.skip(reason="bug to fix")
def test_equals_true1():
    """TODO"""
    filterr = Equals("name", ["va", "2"])
    row = {"name": "value2"}
    assert filterr(row)


def test_equals_false():
    """TODO"""
    filterr = Equals("name", ["va", "2"])
    row = {"name": "value2"}
    assert not filterr(row)


def test_partial_and_true0():
    """TODO"""
    filterr = PartialMultipleAnd(
                {
                    "mail": None,
                    "firstName": None,
                    "lastName": None
                },
                True)
    row = {
        "firstName": "John",
        "lastName": "Do",
        "mail": "jd89@mail.none",
    }
    assert filterr(row)


def test_partial_and_true1():
    """TODO"""
    filterr = PartialMultipleAnd(
                {
                    "mail": None,
                    "firstName": "jo",
                    "lastName": "do"
                },
                True)
    row = {
        "firstName": "John",
        "lastName": "Do",
        "mail": "jd89@mail.none",
    }
    assert filterr(row)


def test_partial_and_true2():
    """TODO"""
    filterr = PartialMultipleAnd(
                {
                    "mail": "8",
                    "firstName": "jo",
                    "lastName": "do"
                },
                True)
    row = {
        "firstName": "John",
        "lastName": "Do",
        "mail": "jd89@mail.none",
    }
    assert filterr(row)


def test_partial_and_true3():
    """TODO"""
    filterr = PartialMultipleAnd(
                {
                    "mail": "89",
                    "firstName": None,
                    "lastName": None
                },
                True)
    row = {
        "firstName": "John",
        "lastName": "Do",
        "mail": "jd89@mail.none",
    }
    assert filterr(row)


def test_partial_and_false1():
    """TODO"""
    filterr = PartialMultipleAnd(
                {
                    "mail": None,
                    "firstName": "jo",
                    "lastName": "doee"
                },
                True)
    row = {
        "firstName": "John",
        "lastName": "Do",
        "mail": "jd89@mail.none",
    }
    assert not filterr(row)


def test_partial_and_false2():
    """TODO"""
    filterr = PartialMultipleAnd(
                {
                    "mail": "3",
                    "firstName": "jo",
                    "lastName": "do"
                },
                True)
    row = {
        "firstName": "John",
        "lastName": "Do",
        "mail": "jd89@mail.none",
    }
    assert not filterr(row)


def test_partial_and_false3():
    """TODO"""
    filterr = PartialMultipleAnd(
                {
                    "mail": "8",
                    "firstName": "jo",
                    "lastName": "do"
                },
                False)
    row = {
        "firstName": "John",
        "lastName": "Do",
        "mail": "jd89@mail.none",
    }
    assert not filterr(row)


def test_partial_and_true4():
    """TODO"""
    filterr = PartialMultipleAnd(
                {
                    "mail": "8",
                    "firstName": "jo",
                    "lastName": "Do"
                },
                False)
    row = {
        "firstName": "John",
        "lastName": "Do",
        "mail": "jd89@mail.none",
    }
    assert not filterr(row)


def test_partial_and_true5():
    """TODO"""
    filterr = PartialMultipleAnd(
                {
                    "mail": None,
                    "firstName": "jo",
                    "lastName": "Do"
                },
                False)
    row = {
        "firstName": "John",
        "lastName": "Do",
        "mail": "jd89@mail.none",
    }
    assert not filterr(row)


def test_partial_date_true0():
    """TODO"""
    filterr = PartialDate("date", None)
    # 2021-07-07 10:52:34
    row = {"name": "value1", "date": 1625647954861, "size": 80000000}
    assert filterr(row)


def test_partial_date_true1():
    """TODO"""
    filterr = PartialDate("date", "2021")
    # 2021-07-07 10:52:34
    row = {"name": "value1", "date": 1625647954861, "size": 80000000}
    assert filterr(row)


def test_partial_date_true2():
    """TODO"""
    filterr = PartialDate("date", "07-07")
    # 2021-07-07 10:52:34
    row = {"name": "value1", "date": 1625647954861, "size": 80000000}
    assert filterr(row)


def test_partial_date_false():
    """TODO"""
    filterr = PartialDate("date", "22")
    # 2021-07-07 10:52:34
    row = {"name": "value1", "date": 1625647954861, "size": 80000000}
    assert not filterr(row)


def test_partial_date_dict_true1():
    """TODO"""
    filterr = PartialDate("date", "2021")
    # 2021-07-07 10:52:34
    row = {"name": "value1", "date": {"k1": "2020", "k2": "2021"}}
    assert filterr(row)


def test_partial_date_dict_true2():
    """TODO"""
    filterr = PartialDate("date", "20")
    # 2021-07-07 10:52:34
    row = {"name": "value1", "date": {"k1": "2020", "k2": "2021"}}
    assert filterr(row)


def test_partial_date_dict_false():
    """TODO"""
    filterr = PartialDate("date", "22")
    # 2021-07-07 10:52:34
    row = {"name": "value1", "date": {"k1": "2020", "k2": "2021"}}
    assert not filterr(row)
