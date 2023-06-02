#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


from argparse import Namespace
from vhatable.factory import TableFactory
from vhatable.factory import GenericBuilder
from vhatable.cellv2 import DateCellBuilder
from vhatable.filters import PartialOr

rows = [
    {"name": "value1", "date": 1625647954855, "size": 80000000},
    {"name": "value2", "date": 1625647954861, "size": 110000},
    {"name": "value3", "date": 1625647954890, "size": 280000000000},
    {"name": "value4", "date": 1625647954905, "size": 21000000000000},
    {"name": "value5", "date": 1625647954962, "size": 2100000000000000},
]


def test_default_processor():
    builder = GenericBuilder(rows=rows)
    factory = TableFactory(builder=builder)
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.set_custom_cell(
            "date", DateCellBuilder("date", millisecond=True))

    args = Namespace(debug=2, reverse=True, sort_by="name")
    processor = factory.build(args)
    processor.column_names = ["name", "size", "date"]

    print()
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 328


def test_vertical_processor():
    builder = GenericBuilder(rows=rows)
    factory = TableFactory(builder=builder)
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.set_custom_cell(
            "date", DateCellBuilder("date", millisecond=True))

    args = Namespace(debug=2, reverse=True, sort_by="name", vertical=True)
    processor = factory.build(args)
    processor.column_names = ["name", "size", "date"]

    print()
    processor.run()
    # rendering is not implemented
    assert len(processor.get_raw()) == 2


def test_count_processor():
    builder = GenericBuilder(rows=rows)
    factory = TableFactory(builder=builder)
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.set_custom_cell(
            "date", DateCellBuilder("date", millisecond=True))

    args = Namespace(debug=2, reverse=True, sort_by="name", count=True)
    processor = factory.build(args)
    processor.column_names = ["name", "size", "date"]

    print()
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 19

    print()
    processor.cli_mode = True
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 1
    assert processor.get_string() == "2"


def test_csv_processor():
    builder = GenericBuilder(rows=rows)
    factory = TableFactory(builder=builder)
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.set_custom_cell(
            "date", DateCellBuilder("date", millisecond=True))

    args = Namespace(debug=2, reverse=True, sort_by="name", csv=True)
    processor = factory.build(args)
    processor.column_names = ["name", "size", "date"]

    print()
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 82

    print()
    processor.csv_headers = False
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 67


def test_json_processor():
    builder = GenericBuilder(rows=rows)
    factory = TableFactory(builder=builder)
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.set_custom_cell(
            "date", DateCellBuilder("date", millisecond=True))

    args = Namespace(debug=2, reverse=True, sort_by="name", json=True)
    processor = factory.build(args)
    processor.column_names = ["name", "size", "date"]

    print()
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 176

    print()
    processor.raw_json = True
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 162
