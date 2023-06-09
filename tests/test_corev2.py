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
from vhatable.processors import HTableProcessor
from vhatable.processors import VTableProcessor
from vhatable.processors import CountProcessor
from vhatable.processors import CsvProcessor
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

    args = Namespace(prefix_debug=2, prefix_reverse=True,
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


@pytest.fixture(name="print_and_count", scope="session")
def fixture_print_and_count(logger):
    """TODO"""
    def inner_print_res(rows):
        res = list(rows)
        logger.info("\nbegin print_and_count")
        cpt = 0
        for row in res:
            cpt += 1
            logger.info("row: %s", row)
        logger.info("end print_and_count")
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


def test_16(logger, print_and_count):
    """TODO"""
    rows = [
            {"name": "value1", "size": 80000000},
            {"name": "value2", "size": 110000},
            {"name": "value3", "size": 280000000000},
            {"name": "value4", "size": 2100000000000000},
    ]
    assert len(rows) == 4
    processor = HTableProcessor(
            debug=3,
            rows=rows,
            column_names=["name", "size"])
    processor.post_init()
    res = processor.get_raw()
    count = print_and_count(res)
    logger.debug(count)
    assert count == 4
    assert len(processor.get_string()) == 159


def test_17():
    """testing horizontal rendering"""
    rows = [
            {"name": "value1", "count": 800000.0001, "size": 80000000},
            {"name": "value2", "count": 8.00001, "size": 110000},
            {"name": "value3", "count": 8000.001, "size": 280000000000},
            {"name": "value4", "count": 800.1, "size": 2100000000000000},
            {"name": "value5 asdqfsdff qsdf   sdf sdf sdf sddf s ",
             "count": 800.1, "size": 2100000000000000},
    ]
    processor = HTableProcessor(
        debug=3,
        rows=rows,
        verbose=True,
        column_names=["name", "size", "unknown column", "count"])
    processor.post_init()
    print("\n")
    processor.run()
    print("\n")
    assert len(processor.get_string()) == 791


def test_18():
    """testing with data but no autokeys and no column names provided"""
    rows = [
            {"name": "value1", "count": 800000.0001, "size": 80000000},
            {"name": "value2", "count": 8.00001, "size": 110000},
            {"name": "value3", "count": 8000.001, "size": 280000000000},
            {"name": "value4", "count": 800.1, "size": 2100000000000000},
            {"name": "value5 asdqfsdff qsdf   sdf sdf sdf sddf s ",
             "count": 800.1, "size": 2100000000000000},
    ]
    processor = HTableProcessor(debug=3, rows=rows, autokeys=False)
    processor.post_init()

    with pytest.raises(ValueError) as exception:
        processor.run()
    msg = "FormattingUnit: Missing required columns to display"
    assert msg in str(exception.value)


def test_19():
    """testing rendering without any data (rows)"""
    processor = HTableProcessor(
        debug=3,
        column_names=["name", "size", "unknown column", "count"])
    processor.post_init()
    print("\n")
    processor.run()
    assert len(processor.get_string()) == 163
    print("\n")


def test_20():
    """testing updates of options in all units"""
    args = Namespace(sort_debug=2, sort_reverse=True, sort_sort_by="name",
                     format_vertical=False, format_extended=True)
    processor = HTableProcessor(debug=3)
    processor.setup(args)
    assert processor.sort.reverse
    assert processor.sort.sort_by == "name"
    assert not processor.format.vertical
    assert processor.format.extended


def test_21():
    """TODO"""
    rows = [
            {"name": "value1", "count": 800000.0001, "size": 80000000},
            {"name": "value2", "count": 8.00001, "size": 110000},
            {"name": "value3", "count": 8000.001, "size": 280000000000},
            {"name": "value4", "count": 800.1, "size": 2100000000000000},
            {"name": "value5 asdqfsdff qsdf   sdf sdf sdf sddf s ",
             "count": 800.1, "size": 2100000000000000},
    ]
    processor = VTableProcessor(
        debug=3,
        rows=rows,
        column_names=["name", "size", "unknown column", "count"])
    processor.post_init()
    print("\n")
    processor.run()
    print("\n")
    assert len(processor.get_raw()) == 5
    assert len(processor.get_string()) == 606


def test_22():
    """testing CountProcessor"""
    rows = [
            {"name": "value1", "count": 800000.0001, "size": 80000000},
            {"name": "value2", "count": 8.00001, "size": 110000},
            {"name": "value3", "count": 8000.001, "size": 280000000000},
            {"name": "value4", "count": 800.1, "size": 2100000000000000},
            {"name": "value5 asdqfsdff qsdf   sdf sdf sdf sddf s ",
             "count": 800.1, "size": 2100000000000000},
    ]
    processor = CountProcessor(
        debug=3,
        rows=rows,
        column_names=["name", "size", "unknown column", "count"])
    processor.post_init()
    print("\n")
    processor.run()
    print("\n")
    assert processor.get_string() == "Ressources found: 5"
    processor.cli_mode = True
    assert processor.get_string() == "5"


def test_23():
    """testing CsvProcessor"""
    rows = [
            {"name": "value1", "count": 800000.0001, "size": 80000000},
            {"name": "value2", "count": 8.00001, "size": 110000},
            {"name": "value3", "count": 8000.001, "size": 280000000000},
            {"name": "value4", "count": 800.1, "size": 2100000000000000},
            {"name": "value5 asdqfsdff qsdf   sdf sdf sdf sddf s ",
             "count": 800.1, "size": 2100000000000000},
    ]
    processor = CsvProcessor(
        debug=3,
        rows=rows,
        column_names=["name", "size", "unknown column", "count"])
    print("\n")
    processor.post_init()
    processor.run()
    print("\n")

    expected = """name;size;unknown column;count
value1;80 MB;-;800000.0001
value2;110 KB;-;8.00001
value3;280 GB;-;8000.001
value4;2.1 PB;-;800.1
value5 asdqfsdff qsdf   sdf sdf sdf sddf s ;2.1 PB;-;800.1"""

    assert str(processor.get_string()) == expected
