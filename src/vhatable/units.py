#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


# This file is part of Vhatable api.
#
# Vhatable api is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Vhatable api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Vhatable api.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2023 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#


import json

from collections import OrderedDict

import prettytable
from .cellv2 import CellBuilderFactory
from .corev2 import Unit


class FilteringUnit(Unit):
    """TODO"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._filters = []
        self._rows = []

    def add(self, *filters):
        """Add some filters."""
        self.log.debug("filters to add: %s", filters)
        for filterr in filters:
            self._filters.append(filterr)
        return self

    def add_if(self, condition, *filters):
        """Add some filters only if condition is true"""
        if condition:
            for filterr in filters:
                self._filters.append(filterr)
        return self

    def matches(self, row):
        """TODO"""
        matches = 0
        enabled_filters = 0
        for func in self._filters:
            if self.debug >= 2:
                self.log.debug("filter: %s (enabled=%s)", func, func.is_enable())
            if func.is_enable():
                enabled_filters += 1
                if func(row):
                    matches += 1
        if self.debug >= 2:
            self.log.debug("matches: %s", matches)
            self.log.debug("enabled_filters: %s", enabled_filters)
        if enabled_filters == 0:
            return True
        if matches == enabled_filters:
            return True
        return False

    def __call__(self, rows):
        self._rows = rows
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("every row should be a dict")
            if self.matches(row):
                yield row


class PassThroughUnit(Unit):
    """TODO"""

    def __call__(self, rows):
        for row in rows:
            yield row


class SortingUnit(Unit):
    """TODO"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reverse = False
        self.sort_by = None
        self._attrs += ["reverse", "sort_by"]

    def __call__(self, rows):
        if self.sort_by:
            try:
                rows = sorted(
                        rows,
                        reverse=self.reverse,
                        key=lambda x: x.get(self.sort_by))
            except KeyError as ex:
                self.log.warning("missing sortby key : %s", ex)
        return rows


class FormattingUnit(Unit):
    """TODO"""
    # pylint: disable=too-many-instance-attributes

    def __init__(self, debug=0, **kwargs):
        super().__init__(debug=debug, **kwargs)
        self.no_cell = False
        self.vertical = False
        self.extended = False
        self.raw_display = False
        self.cfa = CellBuilderFactory()
        self.cfa.debug = debug
        self.required_columns = []
        self.compute_column_for_each_row = False
        self._columns = []
        self._attrs += [
            "raw_display", "no_cell", "vertical", "extended"
        ]
        self._attrs_ro += ["required_columns"]

    @property
    def debug(self):
        """TODO"""
        return self._debug

    @debug.setter
    def debug(self, debug):
        """TODO"""
        self._debug = debug
        self.cfa.debug = debug

    def _get_columns(self, row):
        if self._columns:
            return self._columns

        if not self.required_columns:
            msg = "FormattingUnit: Missing required columns to display"
            raise ValueError(msg)

        def compute(row):
            columns = []
            columns += self.required_columns
            for key in row.keys():
                if key not in columns:
                    columns.append(key)
            return columns
        if self.compute_column_for_each_row:
            return compute(row)
        self._columns = compute(row)
        self.log.debug("columns: %s", self._columns)
        return self._columns

    # pylint: disable=inconsistent-return-statements
    def __call__(self, rows):
        self.log.debug("FormattingUnit:starting converting data to cells")
        if self.no_cell:
            return rows
        for row in rows:
            row_full = OrderedDict()
            for cell_name in self._get_columns(row):
                cell_value = None
                if cell_name in row.keys():
                    cell_value = row[cell_name]
                cell = self.cfa(
                        cell_name, cell_value, context=row_full,
                        extended=self.extended, vertical=self.vertical,
                        raw_display=self.raw_display, hidden=False)
                row_full[cell_name] = cell
            if self.debug >= 2:
                self.log.debug("row_full: %s", row_full)
            yield row_full
        self.log.debug("FormattingUnit:converting data to cells completed.")


class SlicingUnit(Unit):
    """TODO"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.limit = 0
        self.start = 0
        self.end = 0
        self._attrs += ["start", "end", "limit"]

    def __call__(self, rows):
        # flake8: noqa: C901
        self.log.debug("self.start: %s", self.start)
        self.log.debug("self.end: %s", self.end)
        end = 0
        start = 0
        if self.start > 0:
            start = self.start
            if self.limit > 0:
                if self.end > 0:
                    msg = ("can not set 'start',"
                           "'end' and 'limit' at the same time")
                    raise ValueError(msg)
                end = self.start + self.limit
        elif self.end > 0:
            # We need to convert the generator into a list to get the length
            rows = list(rows)
            start = len(rows) - self.end
            if self.limit > 0:
                end = start + self.limit
        elif self.limit > 0:
            end = self.limit
        self.log.debug("start: %s", start)
        self.log.debug("end: %s", end)
        cpt = -1
        for row in rows:
            cpt += 1
            if cpt < start:
                continue
            if end > 0:
                if cpt >= end:
                    break
            yield row


class CollectorUnit(Unit):
    """TODO"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.required_columns = []
        self._attrs += ["required_columns"]

    def __call__(self, rows):
        if not self.required_columns:
            msg = "CollectorUnit: Missing required columns to display"
            raise ValueError(msg)

        for row in rows:
            newrow = []
            for column_name in self.required_columns:
                newrow.append(row.get(column_name))
            self.log.debug("newrow: %s", newrow)
            if newrow:
                yield newrow


class HelloWordRender(Unit):
    """TODO"""

    def __call__(self, rows):
        return "Hello world"


class HeaderRender(Unit):
    """TODO"""

    def __init__(self, identifier="header", typ="render"):
        super().__init__(identifier=identifier, typ=typ)
        self.cli_mode = False
        self._gattrs += ["cli_mode"]
        self.rows = None

    def get_string(self):
        """TODO"""
        return None

    def __call__(self, rows):
        self.rows = rows
        if self.cli_mode:
            return None
        return self.get_string()


class FooterRender(HeaderRender):
    """TODO"""

    def __init__(self, identifier="footer", typ="render"):
        super().__init__(identifier=identifier, typ=typ)


class TableRender(Unit):
    """TODO"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.headers = {}
        self.aligns = {}
        self.cli_mode = False
        self.cli_column_name = None
        self.required_columns = []
        self.columns_to_show = []
        self.table = prettytable.PrettyTable()
        # DEFAULT, PLAIN_COLUMNS, MARKDOWN, ORGMODE, DOUBLE_BORDER
        self.tablefmt = prettytable.SINGLE_BORDER
        self._attrs += ["tablefmt"]
        self._gattrs += ["columns_to_show", "cli_mode"]
        self._attrs_ro += ["required_columns"]

    def get_headers(self):
        """TODO"""
        for column_name in self.columns_to_show:
            if column_name in self.headers:
                yield self.headers.get(column_name)
            else:
                yield column_name

    def build_rows(self, rows):
        """TODO"""
        if not self.columns_to_show:
            msg = "TableRender: Missing required columns to display"
            raise ValueError(msg)
        self.log.debug("columns_to_show: %s", self.columns_to_show)
        for row in rows:
            newrow = []
            for column_name in self.columns_to_show:
                newrow.append(row.get(column_name))
            if newrow:
                yield newrow

    def _get_cli_output(self, rows):
        """TODO"""
        if len(rows) == 0:
            return ""
        if self.cli_column_name is None and self.columns_to_show:
            self.cli_column_name = self.columns_to_show[0]
        if self.cli_column_name is None:
            for key in ["uuid", "UUID", "id", "Id", "ID"]:
                if key in rows[0]:
                    self.cli_column_name = key
        if self.cli_column_name is None:
            raise ValueError("Can not find an identifier in the row. Please provide a column name")
        return "\n".join([str(x.get(self.cli_column_name)) for x in rows])


    def __call__(self, rows):
        if self.cli_mode:
            return self._get_cli_output(rows)
        if not self.columns_to_show:
            self.columns_to_show = list(self.required_columns)
        self.table = prettytable.PrettyTable()
        self.table.set_style(self.tablefmt)
        self.table.field_names = self.get_headers()
        self.table.add_rows(self.build_rows(rows))
        for column_name in self.columns_to_show:
            if column_name in self.aligns:
                self.table.align[column_name] = self.aligns.get(column_name)
            else:
                self.table.align[column_name] = 'c'
        return self.table.get_string()


class CellToJsonUnit(Unit):
    """TODO"""

    def __init__(self, raw=False, dump=True, force_raw=False, **kwargs):
        super().__init__(**kwargs)
        self.required_columns = []
        self.columns_to_show = []
        self.raw = raw
        self.force_raw = force_raw
        self.dump = dump
        self._gattrs += ["columns_to_show"]
        self._attrs += ["required_columns", "raw"]

    def __call__(self, rows):
        if not self.columns_to_show:
            self.columns_to_show = list(self.required_columns)
        if not self.columns_to_show:
            msg = "CellToJsonUnit: Missing required columns to show"
            raise ValueError(msg)

        records = []
        for row in rows:
            record = {}
            for column_name in self.columns_to_show:
                if self.raw or self.force_raw:
                    record[column_name] = row.get(column_name).value
                else:
                    record[column_name] = str(row.get(column_name))
            if self.debug >= 2:
                self.log.debug("record: %s", record)
            records.append(record)
        if self.dump:
            return json.dumps(records, sort_keys=True, indent=2)
        return records


class UpdateRowsUnit(Unit):
    """Generic unit that will update cells.

    Updatable columns will be added as attribute of this class and they will be
    added to the _attrs list, in order to be updated, from args, by the setup method.

    Then, every rows will be updated with these values, in batch.
    """

    def __init__(self, updatable_columns=None, identifier="update", **kwargs):
        super().__init__(identifier=identifier, **kwargs)
        self.updatable_columns = updatable_columns
        self._attrs_ro += ["updatable_columns"]

    @property
    def updatable_columns(self):
        """TODO"""
        return self._updatable_columns

    @updatable_columns.setter
    def updatable_columns(self, updatable_columns):
        """TODO"""
        self._updatable_columns = updatable_columns or []
        for field in self._updatable_columns:
            setattr(self, field, None)
            self._attrs.append(field)

    def __call__(self, rows):
        fields = [field for field in self.updatable_columns if getattr(self, field) is not None]
        if not fields:
            raise ValueError("Can not update. no columns were defined as updatable.")
        for row in rows:
            for field in fields:
                cur_val = getattr(self, field)
                if cur_val is not None:
                    row[field] = cur_val
            yield row
