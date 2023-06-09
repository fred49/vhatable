#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


from argparse import Namespace
import pytest

from vhatable.processors import HTableProcessor
from vhatable.processors import VTableProcessor
from vhatable.processors import CountProcessor
from vhatable.processors import CsvProcessor


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
