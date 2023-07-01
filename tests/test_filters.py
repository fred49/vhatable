#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


from datetime import datetime
from unittest.mock import patch

from vhatable import filtersv2
from vhatable.cell import DateCell
from vhatable.filters import PartialOr
from vhatable.filters import Equal
from vhatable.filters import Equals
from vhatable.filters import PartialMultipleAnd
from vhatable.filters import PartialDate
from vhatable.filtersv2 import EqualMultipleOr
from vhatable.filtersv2 import PartialMultipleAnd as PartialMultipleAndV2
from vhatable.filtersv2 import OlderThanFilter
from vhatable.filtersv2 import NewerThanFilter


def test_nb_filters():
    """TODO"""
    list_filters = [i for i in dir(filtersv2) if not i.startswith("__")]
    list_filters.remove('datetime')
    list_filters.remove('timedelta')
    print(list_filters)
    assert len(list_filters) == 6


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


def test_equals_true2():
    """TODO"""
    filterr = Equals("name", None)
    row = {"name": "value2"}
    assert filterr(row)


def test_equals_true1():
    """TODO"""
    filterr = Equals("name", ["value2", "2"])
    row = {"name": "value2"}
    assert filterr(row)


def test_equals_false():
    """TODO"""
    filterr = Equals("name", ["va", "2"])
    row = {"name": "value2"}
    assert not filterr(row)


def test_equal_or_true0():
    """TODO"""
    filterr = EqualMultipleOr("name", [])
    row = {"name": "value2"}
    assert filterr(row)


def test_equal_or_true2():
    """TODO"""
    filterr = EqualMultipleOr("name", None)
    row = {"name": "value2"}
    assert filterr(row)


def test_equal_or_true1():
    """TODO"""
    filterr = EqualMultipleOr("name", ["value2", "2"])
    row = {"name": "value2"}
    assert filterr(row)


def test_equal_or_false():
    """TODO"""
    filterr = EqualMultipleOr("name", ["va", "2"])
    row = {"name": "value2"}
    assert not filterr(row)


def test_partial_multiple_and_true0():
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


def test_partial_multiple_and_true1():
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


def test_partial_multiple_and_true2():
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


def test_partial_multiple_and_true3():
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


def test_partial_multiple_and_false1():
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


def test_partial_multiple_and_false2():
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


def test_partial_multiple_and_false3():
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


def test_partial_multiple_and_true4():
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


def test_partial_multiple_and_true5():
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


def test_partial_and_false():
    """TODO"""
    filterr = PartialMultipleAndV2("name", ["value2", "value3"])
    row = {"name": "value1"}
    assert not filterr(row)


def test_partial_and_true0():
    """TODO"""
    filterr = PartialMultipleAndV2("name", [])
    row = {"name": "value2"}
    assert filterr(row)


def test_partial_and_true1():
    """TODO"""
    filterr = PartialMultipleAndV2("name", ["val"])
    row = {"name": "value2"}
    assert filterr(row)


def test_partial_and_true2():
    """TODO"""
    filterr = PartialMultipleAndV2("name", ["val", "ue2"])
    row = {"name": "value2"}
    assert filterr(row)


def test_partial_and_true3():
    """TODO"""
    filterr = PartialMultipleAndV2("name", ["kal", "iuu3"])
    row = {"name": "value2"}
    assert not filterr(row)


def test_date_older_than_in_second():
    """TODO"""
    patcher = patch('vhatable.filtersv2.OlderThanFilter._get_today')
    mock_read = patcher.start()
    mock_read.return_value = datetime(2022, 6, 19, 0, 0, 0, 1)

    filterr = OlderThanFilter("date", 3)

    cell = DateCell(datetime(2022, 6, 15, 0, 0, 0, 0).timestamp())
    # input is in seconds
    cell.millisecond = False
    assert filterr({"date": cell})

    cell = DateCell(datetime(2022, 6, 16, 0, 0, 0, 0).timestamp())
    cell.millisecond = False
    assert filterr({"date": cell})

    cell = DateCell(datetime(2022, 6, 17, 0, 0, 0, 0).timestamp())
    cell.millisecond = False
    assert not filterr({"date": cell})


def test_date_older_than_in_millisecond():
    """TODO"""
    patcher = patch('vhatable.filtersv2.OlderThanFilter._get_today')
    mock_read = patcher.start()
    mock_read.return_value = datetime(2022, 6, 19, 0, 0, 0, 1)

    filterr = OlderThanFilter("date", 3)

    cell = DateCell(datetime(2022, 6, 15, 0, 0, 0, 0).timestamp() * 1000)
    assert filterr({"date": cell})

    cell = DateCell(datetime(2022, 6, 16, 0, 0, 0, 0).timestamp() * 1000)
    assert filterr({"date": cell})

    cell = DateCell(datetime(2022, 6, 17, 0, 0, 0, 0).timestamp() * 1000)
    assert not filterr({"date": cell})


def test_date_newer_than_in_second():
    """TODO"""
    patcher = patch('vhatable.filtersv2.NewerThanFilter._get_today')
    mock_read = patcher.start()
    mock_read.return_value = datetime(2022, 6, 19, 0, 0, 0, 1)

    filterr = NewerThanFilter("date", 3)

    cell = DateCell(datetime(2022, 6, 15, 0, 0, 0, 0).timestamp())
    # input is in seconds
    cell.millisecond = False
    assert not filterr({"date": cell})

    cell = DateCell(datetime(2022, 6, 16, 0, 0, 0, 0).timestamp())
    cell.millisecond = False
    assert not filterr({"date": cell})

    cell = DateCell(datetime(2022, 6, 17, 0, 0, 0, 0).timestamp())
    cell.millisecond = False
    assert filterr({"date": cell})


def test_date_newer_than_in_millisecond():
    """TODO"""
    patcher = patch('vhatable.filtersv2.NewerThanFilter._get_today')
    mock_read = patcher.start()
    mock_read.return_value = datetime(2022, 6, 19, 0, 0, 0, 1)

    filterr = NewerThanFilter("date", 3)

    cell = DateCell(datetime(2022, 6, 15, 0, 0, 0, 0).timestamp() * 1000)
    assert not filterr({"date": cell})

    cell = DateCell(datetime(2022, 6, 16, 0, 0, 0, 0).timestamp() * 1000)
    assert not filterr({"date": cell})

    cell = DateCell(datetime(2022, 6, 17, 0, 0, 0, 0).timestamp() * 1000)
    assert filterr({"date": cell})
