#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


from argparse import Namespace
import pytest
from tabulate import tabulate
from veryprettytable import VeryPrettyTable

from vhatable.corev2 import FilteringModule
from vhatable.corev2 import FormattingModule
from vhatable.corev2 import SortingModule
from vhatable.corev2 import SlicingModule
from vhatable.corev2 import BaseTable
from vhatable.filters import PartialOr


def test_1():
    """TODO"""
    filters = FilteringModule()
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
    filters = FilteringModule()
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
    module = SortingModule()
    assert not module.reverse
    assert module.sort_by is None
    assert module.debug == 0

    args = Namespace(debug=2, reverse=True, sort_by="name")
    module.setup_from_args(args)
    assert module.reverse
    assert module.sort_by == "name"
    assert module.debug == 2


def test_3b():
    """TODO"""
    module = SortingModule()
    assert not module.reverse
    assert module.sort_by is None
    assert module.debug == 0

    args = Namespace(debug=2)
    module.setup_from_args(args)
    assert not module.reverse
    assert module.sort_by is None
    assert module.debug == 2


def test_4(logger):
    """TODO"""
    module = SortingModule()
    rows = [
        {"name": "value3"},
        {"name": "value2"},
        {"name": "value4"},
        {"name": "value1"},
    ]
    res = module(list(rows))

    logger.info("aaaa: %s", res)
    assert res == rows


def test_5(logger):
    """TODO"""
    module = SortingModule()
    module.sort_by = "name"
    rows = [
        {"name": "value3"},
        {"name": "value2"},
        {"name": "value4"},
        {"name": "value1"},
    ]
    res = module(rows)

    logger.info("aaaa: %s", res)
    assert res == [{'name': 'value1'}, {'name': 'value2'},
                   {'name': 'value3'}, {'name': 'value4'}]


def test_6(logger):
    """TODO"""
    module = SortingModule()
    module.reverse = True
    module.sort_by = "name"
    rows = [
        {"name": "value3"},
        {"name": "value2"},
        {"name": "value4"},
        {"name": "value1"},
    ]
    res = module(rows)

    logger.info("aaaa: %s", res)
    assert res == [{'name': 'value4'}, {'name': 'value3'},
                   {'name': 'value2'}, {'name': 'value1'}]


def test_7(logger):
    """TODO"""
    module = FormattingModule(debug=3)
    rows = [
            {"name": "value3", "size": 80000000},
            {"name": "value2", "size": 110000},
            {"name": "value4", "size": 280000000000},
            {"name": "value1", "size": 2100000000000000},
    ]
    res = list(module(rows))

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
    module = FormattingModule(debug=3)
    column_names = ["name", "unknown column", "size"]
    module.required_columns = column_names

    table = VeryPrettyTable()
    table.field_names = column_names
    table.align = 'l'
    for row in module(rows):
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
    module = FormattingModule(debug=3)
    column_names = ["name", "unknown column", "size"]
    module.required_columns = column_names
    logger.info(tabulate(rows))


@pytest.fixture(name="print_and_count", scope="session")
def fixture_print_and_count(logger):
    """TODO"""
    def inner_print_res(rows):
        res = list(rows)
        logger.info("")
        cpt = 0
        for row in res:
            cpt += 1
            logger.info("row: %s", row)
        return cpt
    return inner_print_res


def test_10(print_and_count):
    """TODO"""
    rows = [
            {"name": "value1", "size": 80000000},
            {"name": "value2", "size": 110000},
            {"name": "value3", "size": 280000000000},
            {"name": "value4", "size": 2100000000000000},
    ]
    assert len(rows) == 4
    module = SlicingModule(debug=3)
    count = print_and_count(module(iter(rows)))
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
    module = SlicingModule(debug=3)
    module.start = 2
    count = print_and_count(module(iter(rows)))
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
    module = SlicingModule(debug=3)
    module.limit = 1

    res = list(module(iter(rows)))
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
    module = SlicingModule(debug=3)
    module.start = 3
    module.limit = 1

    res = list(module(iter(rows)))
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
    module = SlicingModule(debug=3)
    module.end = 3

    res = list(module(iter(rows)))
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
    module = SlicingModule(debug=3)
    module.end = 3
    module.limit = 1

    res = list(module(iter(rows)))
    count = print_and_count(res)
    assert count == 1
    assert res[0]['name'] == "value2"


def test_16(logger, print_and_count):
    """TODO"""
    rows = [
            {"name": "value1", "size": 80000000},
            {"name": "value2", "size": 110000},
            {"name": "value3", "size": 280000000000},
            {"name": "value4", "size": 2100000000000000},
    ]
    assert len(rows) == 4
    table = BaseTable(debug=3)
    table.load(rows)
    table.column_names = ["name", "size"]
    res = table.get_raw()
    count = print_and_count(res)
    logger.info(type(res))
    assert count == 4
    assert len(table.get_string()) == 274


def test_17():
    """TODO"""
    rows = [
            {"name": "value1", "count": 800000.0001, "size": 80000000},
            {"name": "value2", "count": 8.00001, "size": 110000},
            {"name": "value3", "count": 8000.001, "size": 280000000000},
            {"name": "value4", "count": 800.1, "size": 2100000000000000},
            {"name": "value5 asdqfsdff qsdf   sdf sdf sdf sddf s ",
             "count": 800.1, "size": 2100000000000000},
    ]
    table = BaseTable(debug=3)
    table.column_names = ["name", "size", "unknown column", "count"]
    table.load(rows)
    table.verbose = True
    print("\n")
    table.render()
    print("\n")
    assert len(table.get_string()) == 1221


def test_18():
    """TODO"""
    rows = [
            {"name": "value1", "count": 800000.0001, "size": 80000000},
            {"name": "value2", "count": 8.00001, "size": 110000},
            {"name": "value3", "count": 8000.001, "size": 280000000000},
            {"name": "value4", "count": 800.1, "size": 2100000000000000},
            {"name": "value5 asdqfsdff qsdf   sdf sdf sdf sddf s ",
             "count": 800.1, "size": 2100000000000000},
    ]
    table = BaseTable(debug=3)
    # table.column_names = ["name", "size", "unknown column", "count"]
    table.load(rows)
    print("\n")
    table.render()
    print("\n")
    assert len(table.get_string()) == 0


def test_19():
    """TODO"""
    table = BaseTable(debug=3)
    table.column_names = ["name", "size", "unknown column", "count"]
    print("\n")
    table.render()
    assert len(table.get_string()) == 195
    print("\n")
