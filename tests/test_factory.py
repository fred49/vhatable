#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


from argparse import Namespace
from vhatable.processors import ProcessorFactory
from vhatable.processors import ProcessorBuilder
from vhatable.cellv2 import DateCellBuilder
from vhatable.cellv2 import ComplexCellBuilder
from vhatable.filters import PartialOr

rows = [
    {"name": "value1", "date": 1625647954855, "size": 80000000,
     "uuid": "9390ff25-692c-40eb-af1a-e64302375f67",
     "author": {
         "uuid": "9390ff25-692c-40eb-af1a-e64302375f67",
         "firstname": "Author",
         "lastname": "Name"
     }},
    {"name": "value2", "date": 1625647954861, "size": 110000,
     "uuid": "9413ff25-692c-40eb-af1a-e64302375f67",
     "author": {
         "uuid": "9413ff25-692c-40eb-af1a-e64302375f67",
         "firstname": "Author",
         "lastname": "Name"
     }},
    {"name": "value3", "date": 1625647954890, "size": 280000000000,
     "uuid": "9401ff25-682c-40eb-af4a-e64302375f67",
     "author": {
         "uuid": "9401ff25-682c-40eb-af4a-e64302375f67",
         "firstname": "Author",
         "lastname": "Name"
     }},
    {"name": "value4", "date": 1625647954905, "size": 21000000000000,
     "uuid": "9390ff25-675c-40eb-af48a-e64302375f67",
     "author": {
         "uuid": "9390ff25-675c-40eb-af48a-e64302375f67",
         "firstname": "Author",
         "lastname": "Name"
     }},
    {"name": "value5", "date": 1625647954962, "size": 2100000000000000,
     "author": {
         "uuid": "9391ff25-692c-40eb-af1a-e64302375f67",
         "firstname": "Author",
         "lastname": "Name"
     }},
]


def test_default_processor1():
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date", "author"]
    )
    factory = ProcessorFactory(builder=builder)
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.set_custom_cell(
            "date", DateCellBuilder("date", millisecond=True))
    factory.set_custom_cell(
            "author", ComplexCellBuilder(
                "author",
                fmt='{firstname} {lastname} ({uuid:.8})',
                fmtv='{firstname} {lastname} ({uuid})'
            )
    )

    args = Namespace(debug=2, reverse=True, sort_by="name")
    processor = factory.build(args)

    print()
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 401


def test_vertical_processor():
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date", "author"]
    )
    factory = ProcessorFactory(builder=builder)
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.set_custom_cell(
            "date", DateCellBuilder("date", millisecond=True))
    factory.set_custom_cell(
            "author", ComplexCellBuilder(
                "author",
                fmt='{firstname} {lastname} ({uuid:.8})',
                fmtv='{firstname} {lastname} ({uuid})'
            )
    )
    args = Namespace(debug=2, reverse=True, sort_by="name", vertical=True)
    processor = factory.build(args)

    print()
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 349


def test_count_processor():
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date"]
    )
    factory = ProcessorFactory(builder=builder)
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.set_custom_cell(
            "date", DateCellBuilder("date", millisecond=True))

    args = Namespace(debug=2, reverse=True, sort_by="name", count=True)
    processor = factory.build(args)

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
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date"]
    )
    factory = ProcessorFactory(builder=builder)
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.set_custom_cell(
            "date", DateCellBuilder("date", millisecond=True))

    args = Namespace(debug=2, reverse=True, sort_by="name", csv=True)
    processor = factory.build(args)

    print()
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 82

    print()
    processor.csv_headers = False
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 67


def test_json_processor_formatted():
    """Testing json rendering"""
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date"]
    )
    factory = ProcessorFactory(builder=builder)
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.set_custom_cell(
            "date", DateCellBuilder("date", millisecond=True))

    args = Namespace(debug=2, reverse=True, sort_by="name", json=True)
    processor = factory.build(args)

    print()
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 176


def test_json_processor_raw():
    """Testing raw json rendering"""
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date"]
    )
    factory = ProcessorFactory(builder=builder)
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.set_custom_cell(
            "date", DateCellBuilder("date", millisecond=True))

    args = Namespace(debug=2, reverse=True, sort_by="name", json=True,
                     json_raw=True)
    processor = factory.build(args)

    print()
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 162


def test_default_processor2():
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date", "author"]
    )
    factory = ProcessorFactory(builder=builder)
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.set_custom_cell(
            "date", DateCellBuilder("date", millisecond=True))
    factory.set_custom_cell(
            "author", ComplexCellBuilder(
                "author",
                fmt='{firstname} {lastname} ({uuid:.8})',
                fmtv='{firstname} {lastname} ({uuid})'
            )
    )

    args = Namespace(
            debug=2,
            reverse=True,
            table_required_columns=["name"],
            showindex=False,
            sort_by="name")
    processor = factory.build(args)
    assert processor.table.required_columns == ["name"]

    print()
    print(processor)
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 65


def test_default_processor3():
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date", "author"]
    )
    factory = ProcessorFactory(builder=builder)
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.set_header_cell("date", "Some new header for date column")
    factory.set_custom_cell(
            "date", DateCellBuilder("date", millisecond=True))
    factory.set_custom_cell(
            "author", ComplexCellBuilder(
                "author",
                fmt='{firstname} {lastname} ({uuid:.8})',
                fmtv='{firstname} {lastname} ({uuid})'
            )
    )

    args = Namespace(
            debug=2,
            reverse=True,
            table_required_columns=["name", "date"],
            showindex=True,
            sort_by="name")
    processor = factory.build(args)
    assert processor.table.required_columns == ["name", "date"]

    print()
    print(processor)
    processor.run()
    assert len(processor.get_raw()) == 2
    assert "Some new header for date column" in processor.get_string()
    assert len(processor.get_string()) == 269

    args.vertical = True
    processor = factory.build(args)
    print()
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 403
