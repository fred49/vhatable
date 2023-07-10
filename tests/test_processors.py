#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


from argparse import Namespace
import pytest

from vhatable.processors import HTableProcessor
from vhatable.processors import VTableProcessor
from vhatable.processors import CountProcessor
from vhatable.processors import CsvProcessor
from vhatable.processors import DeleteProcessor
from vhatable.processors import UpdateProcessor
from vhatable.processors import API as AbstractAPI


def test_htable_1(logger, print_and_count):
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


def test_htable_2():
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


def test_htable_3():
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


def test_htable_4():
    """testing rendering without any data (rows)"""
    processor = HTableProcessor(
        debug=3,
        column_names=["name", "size", "unknown column", "count"])
    processor.post_init()
    print("\n")
    processor.run()
    assert len(processor.get_string()) == 163
    print("\n")


def test_htable_5():
    """testing updates of options in all units"""
    args = Namespace(sort_debug=2, sort_reverse=True, sort_sort_by="name",
                     format_vertical=False, format_extended=True)
    processor = HTableProcessor(debug=3)
    processor.setup(args)
    assert processor.sort.reverse
    assert processor.sort.sort_by == "name"
    assert not processor.format.vertical
    assert processor.format.extended


def test_htable_6():
    """testing with data with autokeys and column to show provided"""
    rows = [
            {"name": "value1", "count": 800000.0001, "size": 80000000},
            {"name": "value2", "count": 8.00001, "size": 110000},
            {"name": "value3", "count": 8000.001, "size": 280000000000},
            {"name": "value4", "count": 800.1, "size": 2100000000000000},
    ]
    processor = HTableProcessor(debug=3, rows=rows, autokeys=True)
    processor.post_init()
    args = Namespace(columns_to_show=["name"])
    processor.setup(args)
    print("\n")
    processor.run()
    print("\n")
    assert len(processor.get_string()) == 87


def test_htable_7():
    """testing cli mode"""
    rows = [
            {"id": "6E46010E-9C66-4B99-8412-501000E4F006", "count": 800000.0001, "size": 80000000},
            {"id": "6E46010E-9C66-4B99-8412-501000E4F007", "count": 8.00001, "size": 110000},
            {"id": "6E46010E-9C66-4B99-8412-501000E4F010", "count": 8000.001, "size": 2800000000},
            {"id": "6E46010E-9C66-4B99-8412-501000E4F013", "count": 800.1, "size": 21000000000},
    ]
    processor = HTableProcessor(debug=3, rows=rows, autokeys=True)
    processor.post_init()
    args = Namespace(cli_mode=True)
    processor.setup(args)
    print("\n")
    processor.run()
    print("\n")
    assert len(processor.get_string()) == 147


def test_htable_8():
    """testing cli mode"""
    rows = [
            {"name": "value1", "count": 800000.0001, "size": 80000000},
            {"name": "value2", "count": 8.00001, "size": 110000},
            {"name": "value3", "count": 8000.001, "size": 280000000000},
            {"name": "value4", "count": 800.1, "size": 2100000000000000},
    ]
    processor = HTableProcessor(debug=3, rows=rows, autokeys=True)
    processor.post_init()
    args = Namespace(cli_mode=True, columns_to_show=["name"])
    processor.setup(args)
    print("\n")
    processor.run()
    print("\n")
    assert len(processor.get_string()) == 27


def test_htable_9():
    """testing cli mode"""
    rows = [
            {"name": "value1", "count": 800000.0001, "size": 80000000},
            {"name": "value2", "count": 8.00001, "size": 110000},
            {"name": "value3", "count": 8000.001, "size": 280000000000},
            {"name": "value4", "count": 800.1, "size": 2100000000000000},
    ]
    processor = HTableProcessor(debug=3, rows=rows, autokeys=True)
    processor.post_init()
    args = Namespace(cli_mode=True)
    processor.setup(args)
    with pytest.raises(ValueError) as exception:
        processor.run()
    msg = "Can not find an identifier in the row. Please provide a column name"
    assert msg in str(exception.value)


def test_vertical_table():
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
    assert len(processor.get_string()) == 951


def test_count():
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


def test_csv():
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


def test_delete_processor1():
    """testing DeleteProcessor"""

    class TestAPI(AbstractAPI):
        """TODO"""

        def __init__(self):
            super().__init__()
            self.deleted_cpt = 0

        def list(self):
            """TODO"""
            rows = [
                {"name": "value1", "count": 800000.0001, "size": 80000000},
                {"name": "value2", "count": 8.00001, "size": 110000},
                {"name": "value3", "count": 8000.001, "size": 280000000000},
                {"name": "value4", "count": 800.1, "size": 2100000000000000},
                {"name": "value5 asdqfsdff qsdf   sdf sdf sdf sddf s ",
                 "count": 800.1, "size": 2100000000000000},
            ]
            return rows

        def column_names(self):
            """TODO"""
            return ["name", "count", "unknown", "size"]

        def delete(self, row):
            self.deleted_cpt += 1
            return True, row

    api = TestAPI()
    processor = DeleteProcessor(
        debug=3,
        api=api,
        rows=api.list(),
        column_names=api.column_names())
    print("\n")
    processor.post_init()
    processor.run()
    print("\n")

    assert api.deleted_cpt == 5


def test_delete_processor2():
    """testing DeleteProcessor"""

    class TestAPI(AbstractAPI):
        """TODO"""

        def __init__(self):
            super().__init__()
            self.deleted_cpt = 0
            self.deleted_row = None

        def list(self):
            """TODO"""
            rows = [
                {"name": "value1", "count": 800000.0001, "size": 80000000},
                {"name": "value2", "count": 8.00001, "size": 110000},
                {"name": "value3", "count": 8000.001, "size": 280000000000},
                {"name": "value4", "count": 800.1, "size": 2100000000000000},
                {"name": "value5 asdqfsdff qsdf   sdf sdf sdf sddf s ",
                 "count": 800.1, "size": 2100000000000000},
            ]
            return rows

        def column_names(self):
            """TODO"""
            return ["name", "count", "unknown", "size"]

        def delete(self, row):
            self.deleted_cpt += 1
            self.deleted_row = row
            return True, row

    api = TestAPI()
    processor = DeleteProcessor(
        debug=3,
        api=api,
        rows=api.list(),
        column_names=api.column_names())
    print("\n")
    processor.post_init()
    args = Namespace()
    args.slice_end = 2
    args.slice_limit = 1
    processor.setup(args)
    processor.run()
    print("\n")

    assert api.deleted_cpt == 1
    assert api.deleted_row["name"] == "value4"


def test_update_processor1():
    """testing UpdateProcessor"""

    class TestAPI(AbstractAPI):
        """TODO"""

        def __init__(self):
            super().__init__()
            self.updated_cpt = 0
            self.updated_row = None

        def list(self):
            """TODO"""
            rows = [
                {"name": "value1", "count": 800000.0001, "size": 80000000},
                {"name": "value2", "count": 8.00001, "size": 110000},
                {"name": "value3", "count": 8000.001, "size": 280000000000},
                {"name": "value4", "count": 800.1, "size": 2100000000000000},
                {"name": "value5 asdqfsdff qsdf   sdf sdf sdf sddf s ",
                 "count": 800.1, "size": 2100000000000000},
            ]
            return rows

        def column_names(self):
            """TODO"""
            return ["name", "count", "unknown", "size"]

        def update(self, row):
            self.updated_cpt += 1
            self.updated_row = row
            return True, row

    api = TestAPI()
    processor = UpdateProcessor(
        debug=3,
        api=api,
        rows=api.list(),
        column_names=api.column_names())
    print("\n")
    processor.post_init()
    args = Namespace()
    args.slice_end = 2
    args.slice_limit = 1
    args.update_count = "600"
    processor.setup(args)
    processor.run()
    print("\n")

    assert api.updated_cpt == 1
    assert api.updated_row["name"] == "value4"
    assert api.updated_row["count"] == "600"
