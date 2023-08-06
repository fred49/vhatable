#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


from argparse import Namespace
from vhatable.processors import ProcessorFactory
from vhatable.processors import ProcessorBuilder
from vhatable.cellv2 import DateCellBuilder
from vhatable.cellv2 import ComplexCellBuilder
from vhatable.filters import PartialOr
from vhatable.processors import API as AbstractAPI

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
    """TODO"""
    factory = ProcessorFactory()
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.add_custom_cell(
        DateCellBuilder("date", millisecond=True))
    factory.add_custom_cell(
        ComplexCellBuilder(
            "author",
            fmt='{firstname} {lastname} ({uuid:.8})',
            fmtv='{firstname} {lastname} ({uuid})'
        )
    )
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date", "author"]
    )
    factory.set_default_processor_builder(builder)

    args = Namespace(debug=2, reverse=True, sort_by="name")
    processor = factory.create(args)

    print()
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 401


def test_vertical_processor():
    """TODO"""
    factory = ProcessorFactory()
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.add_custom_cell(
        DateCellBuilder("date", millisecond=True))
    factory.add_custom_cell(
        ComplexCellBuilder(
            "author",
            fmt='{firstname} {lastname} ({uuid:.8})',
            fmtv='{firstname} {lastname} ({uuid})'
        )
    )
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date", "author"]
    )
    factory.set_default_processor_builder(builder)

    args = Namespace(debug=2, reverse=True, sort_by="name", vertical=True)
    processor = factory.create(args)

    print()
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 501


def test_count_processor():
    """TODO"""
    factory = ProcessorFactory()
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.add_custom_cell(
        DateCellBuilder("date", millisecond=True))
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date"]
    )
    factory.set_default_processor_builder(builder)

    args = Namespace(debug=2, reverse=True, sort_by="name", count=True)
    processor = factory.create(args)

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
    """TODO"""
    factory = ProcessorFactory()
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.add_custom_cell(
        DateCellBuilder("date", millisecond=True))
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date"]
    )
    factory.set_default_processor_builder(builder)

    args = Namespace(debug=2, reverse=True, sort_by="name", csv=True)
    processor = factory.create(args)

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
    factory = ProcessorFactory()
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.add_custom_cell(
        DateCellBuilder("date", millisecond=True))
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date"]
    )
    factory.set_default_processor_builder(builder)

    args = Namespace(debug=2, reverse=True, sort_by="name", json=True)
    processor = factory.create(args)

    print()
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 176


def test_json_processor_raw():
    """Testing raw json rendering"""
    factory = ProcessorFactory()
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.add_custom_cell(
        DateCellBuilder("date", millisecond=True))
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date"]
    )
    factory.set_default_processor_builder(builder)

    args = Namespace(debug=2, reverse=True, sort_by="name", json=True,
                     json_raw=True)
    processor = factory.create(args)

    print()
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 162


def test_default_processor2():
    """TODO"""
    factory = ProcessorFactory()
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.add_custom_cell(
        DateCellBuilder("date", millisecond=True))
    factory.add_custom_cell(
        ComplexCellBuilder(
            "author",
            fmt='{firstname} {lastname} ({uuid:.8})',
            fmtv='{firstname} {lastname} ({uuid})'
        )
    )
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date", "author"]
    )
    factory.set_default_processor_builder(builder)

    args = Namespace(
            debug=2,
            reverse=True,
            columns_to_show=["name"],
            showindex=False,
            sort_by="name")
    processor = factory.create(args)
    assert processor.table.columns_to_show == ["name"]

    print()
    print(processor)
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 65


def test_default_processor3():
    """TODO"""
    factory = ProcessorFactory()
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    factory.set_header_cell("date", "Some new header for date column")
    factory.add_custom_cell(
        DateCellBuilder("date", millisecond=True))
    factory.add_custom_cell(
        ComplexCellBuilder(
            "author",
            fmt='{firstname} {lastname} ({uuid:.8})',
            fmtv='{firstname} {lastname} ({uuid})'
        )
    )
    builder = ProcessorBuilder(
        rows=rows,
        column_names=["name", "size", "date", "author"]
    )
    factory.set_default_processor_builder(builder)

    args = Namespace(
            debug=2,
            reverse=True,
            columns_to_show=["name", "date"],
            showindex=True,
            sort_by="name")
    processor = factory.create(args)
    assert processor.table.columns_to_show == ["name", "date"]

    print()
    print(processor)
    processor.run()
    assert len(processor.get_raw()) == 2
    assert "Some new header for date column" in processor.get_string()
    assert len(processor.get_string()) == 269

    args.vertical = True
    processor = factory.create(args)
    print()
    processor.run()
    assert len(processor.get_raw()) == 2
    assert len(processor.get_string()) == 275


class API(AbstractAPI):
    """TODO"""

    def list(self):
        """TODO"""
        some_rows = [
            {"name": "value1", "count": 800000.0001, "size": 80000000},
            {"name": "value3", "count": 8000.001, "size": 280000000000},
            {"name": "value2", "count": 8.00001, "size": 110000},
            {"name": "value4", "count": 800.1, "size": 2100000000000000},
        ]
        return some_rows

    def column_names(self):
        """TODO"""
        return ["name", "count", "unknown", "size"]


def test_default_processor4():
    """TODO"""

    factory = ProcessorFactory()
    factory.set_default_processor_builder(
        ProcessorBuilder(
            api=API(),
            autoload=True
        )
    )

    args = Namespace(
            debug=2,
            sort_by="name")
    processor = factory.create(args)
    assert processor.table.required_columns

    print()
    processor.run()
    assert len(processor.get_raw()) == 4


def test_default_processor5():
    """TODO"""

    api = API()
    factory = ProcessorFactory()
    factory.set_default_processor_builder(
        ProcessorBuilder(
            api=api,
            rows=api.list(),
            column_names=api.column_names()
        )
    )

    args = Namespace(debug=2, sort_by="name")
    processor = factory.create(args)
    assert processor.table.required_columns

    print()
    processor.run()
    assert len(processor.get_raw()) == 4
    assert len(processor.get_string()) == 351


def test_default_processor6():
    """TODO"""

    api = API()
    factory = ProcessorFactory()
    factory.set_default_processor_builder(
        ProcessorBuilder(
            api=api,
            rows=api.list,
            column_names=api.column_names
        )
    )

    args = Namespace(debug=2, sort_by="name")
    processor = factory.create(args)
    assert processor.table.required_columns

    print()
    processor.run()
    assert len(processor.get_raw()) == 4
    assert len(processor.get_string()) == 351


def test_default_processor7():
    """TODO"""

    api = API()
    factory = ProcessorFactory()
    factory.set_default_processor_builder(
        ProcessorBuilder(
            api=api,
            rows=api.list,
            column_names=api.column_names
        )
    )

    args = Namespace(debug=2, sort_by="name")
    processor = factory.create(args)
    processor.run()
    assert len(processor.get_raw()) == 4
    assert len(processor.get_string()) == 351

    factory.default_processor_identifier = "vertical"
    processor = factory.create(args)
    processor.run()
    assert len(processor.get_raw()) == 4
    assert len(processor.get_string()) == 605
