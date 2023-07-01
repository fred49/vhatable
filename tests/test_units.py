#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


from argparse import Namespace
import pytest
from prettytable import PrettyTable
from veryprettytable import VeryPrettyTable

from vhatable.units import FilteringUnit
from vhatable.units import FormattingUnit
from vhatable.units import SortingUnit
from vhatable.units import SlicingUnit
from vhatable.filters import PartialOr


def test_1():
    """TODO"""
    filters = FilteringUnit()
    filters.add(PartialOr("name", ["value2", "value3"], True))
    rows = iter([
        {"name": "value1"},
        {"name": "value2"},
        {"name": "value3"},
        {"name": "value4"},
    ])
    assert not filters.matches(next(rows))
    assert filters.matches(next(rows))
    assert filters.matches(next(rows))
    assert not filters.matches(next(rows))


def test_2():
    """TODO"""
    filters = FilteringUnit()
    filters.add(PartialOr("name", ["value2", "value3"], True))
    rows = [
        {"name": "value1"},
        {"name": "value2"},
        {"name": "value3"},
        {"name": "value4"},
    ]
    data = filters(rows)
    assert list(data) == [{"name": "value2"}, {"name": "value3"}]


def test_3():
    """TODO"""
    unit = SortingUnit()
    assert not unit.reverse
    assert unit.sort_by is None
    assert unit.debug == 0

    args = Namespace(debug=2, reverse=True, sort_by="name")
    unit.setup(args)
    assert unit.reverse
    assert unit.sort_by == "name"
    assert unit.debug == 2


def test_3b():
    """TODO"""
    unit = SortingUnit(identifier="prefix")
    assert not unit.reverse
    assert unit.sort_by is None
    assert unit.debug == 0

    args = Namespace(debug=2, prefix_reverse=True,
                     prefix_sort_by="name")
    unit.setup(args)
    assert unit.reverse
    assert unit.sort_by == "name"
    assert unit.debug == 2


def test_4(logger):
    """TODO"""
    unit = SortingUnit()
    rows = [
        {"name": "value3"},
        {"name": "value2"},
        {"name": "value4"},
        {"name": "value1"},
    ]
    res = unit(list(rows))

    logger.info("aaaa: %s", res)
    assert res == rows


def test_5(logger):
    """TODO"""
    unit = SortingUnit()
    unit.sort_by = "name"
    rows = [
        {"name": "value3"},
        {"name": "value2"},
        {"name": "value4"},
        {"name": "value1"},
    ]
    res = unit(rows)

    logger.info("aaaa: %s", res)
    assert res == [{'name': 'value1'}, {'name': 'value2'},
                   {'name': 'value3'}, {'name': 'value4'}]


def test_6(logger):
    """TODO"""
    unit = SortingUnit()
    unit.reverse = True
    unit.sort_by = "name"
    rows = [
        {"name": "value3"},
        {"name": "value2"},
        {"name": "value4"},
        {"name": "value1"},
    ]
    res = unit(rows)

    logger.info("aaaa: %s", res)
    assert res == [{'name': 'value4'}, {'name': 'value3'},
                   {'name': 'value2'}, {'name': 'value1'}]


def test_7(logger):
    """TODO"""
    unit = FormattingUnit(debug=3)
    rows = [
            {"name": "value3", "size": 80000000},
            {"name": "value2", "size": 110000},
            {"name": "value4", "size": 280000000000},
            {"name": "value1", "size": 2100000000000000},
    ]
    unit.required_columns = ["name", "size"]
    res = list(unit(rows))

    for row in res:
        logger.info("cell: %s", row)

    assert res[0]['name'].value == "value3"
    assert res[0]['size'].value == 80000000
    assert str(res[0]['size']) == "80 MB"


def test_8(logger):
    """TODO"""
    rows = [
            {"name": "value3", "size": 80000000},
            {"name": "value2", "size": 110000},
            {"name": "value4", "size": 280000000000},
            {"name": "value1", "size": 2100000000000000},
    ]
    unit = FormattingUnit(debug=3)
    column_names = ["name", "unknown column", "size"]
    unit.required_columns = column_names

    table = VeryPrettyTable()
    table.field_names = column_names
    table.align = 'l'
    for row in unit(rows):
        data = []
        for colum in row.keys():
            data.append(row.get(colum))
        table.add_row(data)
    logger.info(table.get_string())


def test_9(logger):
    """TODO"""
    rows = [
            {"name": "value3", "size": 80000000},
            {"name": "value2", "size": 110000},
            {"name": "value4", "size": 280000000000},
            {"name": "value1", "size": 2100000000000000},
    ]
    unit = FormattingUnit(debug=3)
    column_names = ["name", "unknown column", "size"]
    unit.required_columns = column_names
    table = PrettyTable()
    table.add_rows(rows)
    logger.info(table)


def test_10(print_and_count):
    """TODO"""
    rows = [
            {"name": "value1", "size": 80000000},
            {"name": "value2", "size": 110000},
            {"name": "value3", "size": 280000000000},
            {"name": "value4", "size": 2100000000000000},
    ]
    assert len(rows) == 4
    unit = SlicingUnit(debug=3)
    count = print_and_count(unit(iter(rows)))
    assert count == 4


def test_11(print_and_count):
    """TODO"""
    rows = [
            {"name": "value1", "size": 80000000},
            {"name": "value2", "size": 110000},
            {"name": "value3", "size": 280000000000},
            {"name": "value4", "size": 2100000000000000},
    ]
    assert len(rows) == 4
    unit = SlicingUnit(debug=3)
    unit.start = 2
    count = print_and_count(unit(iter(rows)))
    assert count == 2


def test_12(print_and_count):
    """TODO"""
    rows = [
            {"name": "value1", "size": 80000000},
            {"name": "value2", "size": 110000},
            {"name": "value3", "size": 280000000000},
            {"name": "value4", "size": 2100000000000000},
    ]
    assert len(rows) == 4
    unit = SlicingUnit(debug=3)
    unit.limit = 1

    res = list(unit(iter(rows)))
    count = print_and_count(res)
    assert count == 1
    assert res[0]['name'] == "value1"


def test_13(print_and_count):
    """TODO"""
    rows = [
            {"name": "value1", "size": 80000000},
            {"name": "value2", "size": 110000},
            {"name": "value3", "size": 280000000000},
            {"name": "value4", "size": 2100000000000000},
    ]
    assert len(rows) == 4
    unit = SlicingUnit(debug=3)
    unit.start = 3
    unit.limit = 1

    res = list(unit(iter(rows)))
    count = print_and_count(res)
    assert count == 1
    assert res[0]['name'] == "value4"


def test_14(print_and_count):
    """TODO"""
    rows = [
            {"name": "value1", "size": 80000000},
            {"name": "value2", "size": 110000},
            {"name": "value3", "size": 280000000000},
            {"name": "value4", "size": 2100000000000000},
    ]
    assert len(rows) == 4
    unit = SlicingUnit(debug=3)
    unit.end = 3

    res = list(unit(iter(rows)))
    count = print_and_count(res)
    assert count == 3
    assert res[0]['name'] == "value2"
    assert res[1]['name'] == "value3"
    assert res[2]['name'] == "value4"


def test_15(print_and_count):
    """TODO"""
    rows = [
            {"name": "value1", "size": 80000000},
            {"name": "value2", "size": 110000},
            {"name": "value3", "size": 280000000000},
            {"name": "value4", "size": 2100000000000000},
    ]
    assert len(rows) == 4
    unit = SlicingUnit(debug=3)
    unit.end = 3
    unit.limit = 1

    res = list(unit(iter(rows)))
    count = print_and_count(res)
    assert count == 1
    assert res[0]['name'] == "value2"
