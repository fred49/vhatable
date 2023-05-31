#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Contains cell builders and factory to handle rendering in a table."""


# This file is part of Vhatable cli.
#
# Vhatable cli is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Vhatable cli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Vhatable cli.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2019 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#


import logging

from .cell import SCell, BCell, ICell
from .cell import SizeCell
from .cell import DateCell
from .cell import TypeCell
from .cell import ComplexCell


class CellBuilder:
    """A helper to configure and build a cell."""
    # pylint: disable=too-few-public-methods
    # pylint: disable=[too-many-arguments]

    clazz = None

    def __init__(self, cell_name, fmt=None, fmtv=None, fmtf=None,
                 none="-", clazz=None):
        """Create a builder:

        :param str cell_name: coucou
        :param str none: giggiggigi
        """
        self.none = none
        self.cell_name = cell_name
        if clazz is not None:
            self.clazz = clazz
        self.fmt = fmt
        self.fmt_vertical = fmtv
        self.fmt_for_filtering = fmtf

    def __call__(self, cell_value, raw_display=False, vertical=False,
                 extended=False, hidden=False, context=None):
        """Build and return a new cell"""
        cell = self.clazz(cell_value)
        cell.name = self.cell_name
        if self.fmt is not None:
            cell.formatt = self.fmt
        if self.fmt_vertical is not None:
            cell.formatv = self.fmt_vertical
        if self.fmt_for_filtering is not None:
            cell.formatf = self.fmt_for_filtering
        cell.raw = raw_display
        cell.vertical = vertical
        cell.extended = extended
        cell.hidden = hidden
        if context is not None:
            cell.row = context
        return self._post_build(cell)

    def _post_build(self, cell):
        """Hook use to enhance cell with extra property once created."""
        # pylint: disable=no-self-use
        return cell


class StringCellBuilder(CellBuilder):
    """Builder for a StringCell (SCell)"""
    # pylint: disable=too-few-public-methods

    clazz = SCell


class IntCellBuilder(CellBuilder):
    """Builder for a ICell"""
    # pylint: disable=too-few-public-methods

    clazz = ICell


class BoolCellBuilder(CellBuilder):
    """Builder for a BCell"""
    # pylint: disable=too-few-public-methods

    clazz = BCell


class DateCellBuilder(CellBuilder):
    """Builder for a DateCell"""
    # pylint: disable=too-few-public-methods

    clazz = DateCell

    def __init__(self, *args, millisecond=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.millisecond = millisecond

    def _post_build(self, cell):
        """TODO"""
        cell.millisecond = self.millisecond
        return cell


class SizeCellBuilder(CellBuilder):
    """Builder for a SizeCell"""
    # pylint: disable=too-few-public-methods

    clazz = SizeCell


class TypeCellBuilder(CellBuilder):
    """Builder for a TypeCell.
    It will just render type of the content of the cell.
    Could be used for debug."""
    # pylint: disable=too-few-public-methods

    clazz = TypeCell


class ComplexCellBuilder(CellBuilder):
    """Builder for a ComplexCell.
    A complex cell is a json."""
    # pylint: disable=too-few-public-methods

    clazz = ComplexCell


class CellBuilderFactory:
    """TODO"""
    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        self.raw_display = False
        self.debug = 0
        self.vertical = False
        classname = str(self.__class__.__name__.lower())
        self.log = logging.getLogger("vhatablecli.cellv2." + classname)
        self.date_cells = [
            "creationDate",
            "modificationDate",
            "expirationDate",
            "uploadDate"
        ]
        self.size_cells = ["size"]
        self.custom_cells = {}

    def get_cell_builder(self, cell_name, cell_value):
        """Return the cell builder accoring the configuration or type of
        the input cell_value.
        """
        builder_clazz = None
        if cell_name in self.date_cells:
            builder_clazz = DateCellBuilder
        elif cell_name in self.size_cells:
            builder_clazz = SizeCellBuilder
        elif isinstance(cell_value, bool):
            builder_clazz = BoolCellBuilder
        elif isinstance(cell_value, int):
            builder_clazz = IntCellBuilder
        elif isinstance(cell_value, list):
            builder_clazz = ComplexCellBuilder
        elif isinstance(cell_value, dict):
            builder_clazz = ComplexCellBuilder
        else:
            builder_clazz = StringCellBuilder
        return builder_clazz(cell_name)

    def __call__(self, cell_name, cell_value, context=None,
                 extended=False, vertical=None, hidden=False,
                 raw_display=None):
        if vertical is not None:
            self.vertical = vertical
        if raw_display is not None:
            self.raw_display = raw_display
        if cell_name in self.custom_cells:
            builder = self.custom_cells.get(cell_name)
        else:
            builder = self.get_cell_builder(cell_name, cell_value)
        if self.debug >= 2:
            self.log.debug("building cell ...")
            self.log.debug("builder: %s", builder)
            self.log.debug("name: %s, type: %s", cell_name, type(cell_value))
            self.log.debug("cell_value: %s", cell_value)
            self.log.debug("raw_display: %s", self.raw_display)
            self.log.debug("vertical: %s", self.vertical)
        cell = builder(
                cell_value,
                raw_display=self.raw_display,
                vertical=self.vertical,
                extended=extended,
                hidden=hidden,
                context=context)
        if self.debug >= 3:
            self.log.debug("cell type: %s", type(cell))
            # str method from all cell must return encoded strings
            self.log.debug("cell rendering: %s", str(cell))
            self.log.debug("cell built.")
        return cell
