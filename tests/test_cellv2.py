#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Testing actions like rsync, hard links, ..."""


from vhatable.cellv2 import BoolCellBuilder
from vhatable.cellv2 import IntCellBuilder
from vhatable.cellv2 import DateCellBuilder
from vhatable.cellv2 import StringCellBuilder
from vhatable.cellv2 import SizeCellBuilder
from vhatable.cellv2 import ComplexCellBuilder
from vhatable.cellv2 import TypeCellBuilder
from vhatable.cellv2 import CellBuilderFactory


def test_bool_true(logger):
    """Testing boolean builder"""
    # pylint: disable=redefined-outer-name
    builder = BoolCellBuilder("isBlue")
    cell = builder(
            True,
            raw_display=False,
            vertical=False,
            extended=False,
            hidden=False)
    logger.info("cell: %s", cell)
    assert str(cell) == "True"
    assert cell.name == "isBlue"
    assert not cell.raw
    assert not cell.vertical
    assert not cell.extended
    assert not cell.hidden


def test_bool_false(logger):
    """Testing boolean builder"""
    # pylint: disable=redefined-outer-name
    builder = BoolCellBuilder("isBlue")
    cell = builder(
            False,
            raw_display=True,
            vertical=True,
            extended=True,
            hidden=True)
    logger.info("cell: %s", cell)
    assert str(cell) == "False"
    assert cell.name == "isBlue"
    assert cell.raw
    assert cell.vertical
    assert cell.extended
    assert cell.hidden


def test_int(logger):
    """Testing int builder"""
    builder = IntCellBuilder("count")
    cell = builder(8)
    logger.info("cell: %s", cell)
    assert cell.value == 8
    assert str(cell) == "8"


def test_string(logger):
    """Testing int builder"""
    builder = StringCellBuilder("count")
    cell = builder("77 aa")
    logger.info("cell: %s", cell)
    assert cell.value == "77 aa"
    assert str(cell) == "77 aa"


def test_date():
    """Testing date builder"""
    builder = DateCellBuilder("creationDate", millisecond=False)
    assert not builder.millisecond
    cell = builder(1685211807.637026)
    assert not cell.millisecond
    assert str(cell) == "2023-05-27 20:23:27"
    assert cell.value == 1685211807.637026


def test_date2():
    """Testing date builder"""
    builder = DateCellBuilder("creationDate", millisecond=True)
    assert builder.millisecond
    cell = builder(1685211807.637026 * 1000)
    assert cell.millisecond
    assert cell.value == 1685211807637.0261
    assert str(cell) == "2023-05-27 20:23:27"


def test_date3():
    """Testing date builder"""
    fmt = "{da:%Y-%m-%d}"
    builder = DateCellBuilder(
            "creationDate",
            millisecond=True,
            fmt=fmt)
    assert fmt == builder.fmt
    cell = builder(1685211807.637026 * 1000)
    # pylint: disable=protected-access
    assert fmt == cell._format
    assert cell.value == 1685211807637.0261
    assert str(cell) == "2023-05-27"


def test_date4():
    """Testing date builder"""
    fmt = "{da:%Y-%m-%d} horizontal"
    fmtv = "{da:%Y-%m-%d} vertical"
    builder = DateCellBuilder(
            "creationDate",
            millisecond=True,
            fmt=fmt,
            fmtv=fmtv)
    assert fmt == builder.fmt
    assert fmtv == builder.fmt_vertical

    value = 1685211807.637026 * 1000

    cell = builder(value)
    # pylint: disable=protected-access
    assert fmt == cell._format
    assert fmtv == cell._format_vertical
    assert cell.value == 1685211807637.0261
    assert str(cell) == "2023-05-27 horizontal"

    cell = builder(value, vertical=True)
    assert cell.value == 1685211807637.0261
    assert str(cell) == "2023-05-27 vertical"


def test_date5():
    """Testing date builder"""
    fmt = "{da:%Y-%m-%d} horizontal"
    fmtf = "{da:%Y-%m-%d} filter"
    builder = DateCellBuilder(
            "creationDate",
            millisecond=True,
            fmt=fmt,
            fmtf=fmtf)
    assert fmt == builder.fmt
    assert fmtf == builder.fmt_for_filtering

    value = 1685211807.637026 * 1000

    cell = builder(value, raw_display=True)
    # pylint: disable=protected-access
    assert cell._format == fmt
    assert cell._format_vertical == "{da:%Y-%m-%d %H:%M:%S}"
    assert cell._format_filter == fmtf
    assert cell.value == 1685211807637.0261
    assert str(cell) == "1685211807637.0261"


def test_type(logger):
    """Testing int builder"""
    builder = TypeCellBuilder("count")
    cell = builder(8)
    logger.info("cell: %s", cell)
    assert cell.value == 8
    assert str(cell) == "<class 'int'>"


def test_size(logger):
    """Testing int builder"""
    builder = SizeCellBuilder("size")
    cell = builder(2000)
    logger.info("cell: %s", cell)
    assert cell.value == 2000
    assert str(cell) == "2 KB"


def test_complex(logger):
    """Testing int builder"""
    builder = ComplexCellBuilder("author")
    value = {
        "uuid": "dddddddd",
        "firstname": "Author",
        "lastname": "Name"
    }
    cell = builder(value)
    logger.info("cell: %s", cell)
    assert cell.value == value
    res = "{'uuid': 'dddddddd', 'firstname': 'Author', 'lastname': 'Name'}"
    assert str(cell) == res


def test_complex2(logger):
    """Testing int builder"""
    builder = ComplexCellBuilder(
            "author",
            fmt='{firstname} {lastname} ({uuid:.8})',
            fmtv='{firstname} {lastname} ({uuid})'
    )
    value = {
        "uuid": "126a2a2e-82b5-47e7-8948-6110c8b702be",
        "firstname": "Author",
        "lastname": "Name"
    }
    cell = builder(value)
    logger.info("cell: %s", cell)
    assert cell.value == value
    assert str(cell) == "Author Name (126a2a2e)"

    cell = builder(value, vertical=True)
    logger.info("cell: %s", cell)
    assert cell.value == value
    assert str(cell) == "Author Name (126a2a2e-82b5-47e7-8948-6110c8b702be)"

    cell = builder(value, raw_display=True)
    logger.info("cell: %s", cell)
    assert cell.value == value
    assert str(cell) == str(value)


def test_factory1(logger):
    """Testing factory"""
    cell_name = "size"
    cell_value = 2000

    cfa = CellBuilderFactory()
    logger.info("cfa: %s", cfa)

    cell = cfa(cell_name, cell_value)
    logger.info("cell: %s", cell)
    assert isinstance(cell, SizeCellBuilder.clazz)


def test_factory2(logger):
    """Testing factory"""
    cell_name = "creationDate"
    cell_value = 1685211807.637026

    cfa = CellBuilderFactory()
    logger.info("cfa: %s", cfa)

    cell = cfa(cell_name, cell_value)
    logger.info("cell: %s", cell)
    assert isinstance(cell, DateCellBuilder.clazz)


def test_factory3(logger):
    """Testing factory"""
    cell_name = "a_list_value"
    cell_value = [1, 2, 3, 4]

    cfa = CellBuilderFactory()
    logger.info("cfa: %s", cfa)

    cell = cfa(cell_name, cell_value)
    logger.info("cell: %s", cell)
    assert isinstance(cell, ComplexCellBuilder.clazz)


def test_factory4(logger):
    """Testing factory"""
    cell_name = "isBlue"
    cell_value = True

    cfa = CellBuilderFactory()
    logger.info("cfa: %s", cfa)

    cell = cfa(cell_name, cell_value)
    logger.info("cell: %s", cell)
    assert isinstance(cell, BoolCellBuilder.clazz)


def test_factory5(logger):
    """Testing factory"""
    cell_name = "count"
    cell_value = 99

    cfa = CellBuilderFactory()
    logger.info("cfa: %s", cfa)

    cell = cfa(cell_name, cell_value)
    logger.info("cell: %s", cell)
    assert isinstance(cell, IntCellBuilder.clazz)


def test_factory6(logger):
    """Testing factory"""
    cell_name = "isBlue"
    cell_value = "ddd"

    cfa = CellBuilderFactory()
    logger.info("cfa: %s", cfa)

    cell = cfa(cell_name, cell_value)
    logger.info("cell: %s", cell)
    assert isinstance(cell, StringCellBuilder.clazz)


def test_factory7(logger):
    """Testing factory"""
    cell_name = "dict_value"
    cell_value = {"a": 1, "b": 2}

    cfa = CellBuilderFactory()
    logger.info("cfa: %s", cfa)

    cell = cfa(cell_name, cell_value)
    logger.info("cell: %s", cell)
    assert isinstance(cell, ComplexCellBuilder.clazz)


def test_factory8(logger):
    """Testing factory"""
    cell_name = "foobar"
    cell_value = 1685211807.637026

    cfa = CellBuilderFactory()
    builder = DateCellBuilder("foobar", millisecond=True)
    cfa.custom_cells['foobar'] = builder
    logger.info("cfa: %s", cfa)

    cell = cfa(cell_name, cell_value)
    logger.info("cell: %s", cell)
    assert isinstance(cell, DateCellBuilder.clazz)
