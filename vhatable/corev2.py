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


import time
import json
import logging
import prettytable

from collections import OrderedDict
from functools import wraps

from .cellv2 import CellBuilderFactory


class Time:
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self,
                 logger_name,
                 label="execution time: {time:.15f}"):
        self.log = logging.getLogger(logger_name)
        self.enabled = False
        self.label = label

    def __call__(self, original_func):
        @wraps(original_func)
        def time_wrapper(*args, **kwargs):
            self.log.debug("args: %s", args)
            self.log.debug("kwargs: %s", kwargs)
            start = time.time()
            res = original_func(*args, **kwargs)
            end = time.time()
            if len(args) > 0:
                first_arg = args[0]
                self.enabled = getattr(first_arg, "verbose", self.enabled)
            diff = end - start
            msg = self.label.format(time=diff)
            self.log.debug(msg)
            if self.enabled:
                print(msg)
            return res
        return time_wrapper


class Unit:
    """TODO"""

    def __init__(self, typ="transform",  debug=0, identifier=None):
        self.log = logging.getLogger(__name__)
        self._debug = debug
        self.identifier = identifier
        self._attrs = ["debug"]
        self.typ = typ

    @property
    def debug(self):
        """TODO"""
        return self._debug

    @debug.setter
    def debug(self, debug):
        """TODO"""
        self._debug = debug

    def setup(self, from_args):
        """TODO"""
        for attr in self._attrs:
            if self.identifier:
                attr_with_prefix = self.identifier + "_" + attr
                if hasattr(from_args, attr_with_prefix):
                    setattr(self, attr, getattr(from_args, attr_with_prefix))
            else:
                if hasattr(from_args, attr):
                    setattr(self, attr, getattr(from_args, attr))
            self.log.debug("setup:attr: %s : %s", attr, getattr(self, attr))
        return self

    def __str__(self):
        rows = []
        prefix = ""
        if self.identifier:
            prefix = self.identifier + "_"

        rows.append("Unit: " + self.__class__.__name__ + ":")
        for attr in self._attrs:
            attr_val = getattr(self, attr)
            rows.append(f" - {prefix}{attr}: {attr_val}")
        rows.append("")
        return "\n".join(rows)


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
            self.log.debug("filter: %s (enabled=%s)", func, func.is_enable())
            if func.is_enable():
                enabled_filters += 1
                if func(row):
                    matches += 1
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
            "raw_display", "no_cell", "vertical", "extended",
            "required_columns"
        ]

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
            self.log.debug("row_full: %s", row_full)
            yield row_full


class SlicingUnit(Unit):
    """TODO"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.limit = 0
        self.start = 0
        self.end = 0
        self._attrs += ["start", "end", "limit"]

    def __call__(self, rows):
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


class AbstractProcessor:
    """TODO"""

    def __init__(self, debug=0, verbose=False, rows=None, column_names=None,
                 autokeys=True):
        self._attrs = ["debug", "verbose", "column_names"]
        classname = str(self.__class__.__name__.lower())
        self.log = logging.getLogger('vhatable.' + classname)
        self.units = OrderedDict()
        self.column_names = []
        self._auto_columns = False
        self._rows = []
        self._raw_cache = None
        self._post_init = False
        self.messages = {}
        self.debug = debug
        self.verbose = verbose
        if rows:
            self._rows = rows
        if column_names:
            self.column_names = column_names
        elif autokeys:
            if rows and len(rows) >= 1:
                self.column_names = rows[0].keys()

    def add_transform_unit(self, identifier, unit):
        """TODO"""
        self.units[identifier] = unit(identifier=identifier, typ="transform")

    def add_render_unit(self, identifier, unit):
        """TODO"""
        self.units[identifier] = unit(identifier=identifier, typ="render")

    def post_init(self):
        """TODO"""
        self._post_init = True

    def __getattr__(self, attr):
        if attr in self.units:
            return self.units[attr]
        classname = self.__class__.__name__
        raise AttributeError(f"'{classname}' object has no attribute '{attr}'")

    def __str__(self):
        rows = []
        rows.append("Processor - " + self.__class__.__name__ + ":")
        for attr in self._attrs:
            attr_val = getattr(self, attr)
            rows.append(f" - {attr}: {attr_val}")
        rows.append("")
        for unit in self.units.values():
            rows.append(str(unit))
        return "\n".join(rows)

    def pre_get_raw_hook(self):
        pass

    def get_raw(self):
        """TODO"""
        if self._raw_cache is not None:
            self.log.debug("cached rows: %s", self._raw_cache)
            return self._raw_cache
        if not self._post_init:
            raise ValueError("post_init method was not called.")
        self.log.debug("Units: %s", self.units)
        self.log.debug("Rows: %s", self._rows)
        self.pre_get_raw_hook()
        pipeline = self._rows
        for unit in self.units.values():
            if unit.typ == "transform":
                self.log.debug("unit: %s", unit)
                pipeline = unit(pipeline)
        self._raw_cache = list(pipeline)
        self.log.debug("pipeline rows: %s", self._raw_cache)
        return self._raw_cache

    def load(self, rows):
        """TODO"""
        self._rows = rows
        return self

    def get_string(self):
        """TODO"""
        result = []
        for unit in self.units.values():
            self.log.debug("unit: %s", unit)
            if unit.typ == "render":
                self.log.debug("unit:render: %s", unit)
                result.append(unit(self.get_raw()))
        return "\n".join(result)

    def setup(self, from_args):
        """TODO"""
        self.post_init()
        for attr in self._attrs:
            if hasattr(from_args, attr):
                setattr(self, attr, getattr(from_args, attr))
            self.log.debug("setup:attr: %s : %s", attr, getattr(self, attr))
        for unit in self.units.values():
            self.log.debug("unit: %s", unit)
            unit.setup(from_args)
        return self

    @Time('vhatable.corev2.run')
    def run(self):
        """TODO"""
        print(self.get_string())
        return True


class Processor(AbstractProcessor):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_transform_unit('format', FormattingUnit)
        self.add_transform_unit('filter', FilteringUnit)
        self.add_transform_unit('sort', SortingUnit)
        self.add_transform_unit('slice', SlicingUnit)

    def setup(self, from_args):
        """TODO"""
        if 'format' in self.units:
            self.units['format'].vertical = getattr(
                    from_args, "vertical", False)
        super().setup(from_args)
        return self

    def post_init(self):
        """TODO"""
        self._post_init = True
        if 'format' in self.units:
            self.units['format'].required_columns = self.column_names


class TableRender(Unit):
    """TODO"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.headers = {}
        self.aligns = {}
        self.required_columns = []
        # DEFAULT, PLAIN_COLUMNS, MARKDOWN, ORGMODE, DOUBLE_BORDER
        self.tablefmt = prettytable.SINGLE_BORDER
        self._attrs += ["tablefmt", "required_columns"]

    def get_headers(self):
        """TODO"""
        for column_name in self.required_columns:
            if column_name in self.headers:
                yield self.headers.get(column_name)
            else:
                yield column_name

    def build_rows(self, rows):
        """TODO"""
        if not self.required_columns:
            msg = "TableRender: Missing required columns to display"
            raise ValueError(msg)
        for row in rows:
            newrow = []
            for column_name in self.required_columns:
                newrow.append(row.get(column_name))
            self.log.debug("newrow: %s", newrow)
            if newrow:
                yield newrow

    def __call__(self, rows):
        table = prettytable.PrettyTable()
        table.set_style(self.tablefmt)
        table.field_names = self.get_headers()
        table.add_rows(self.build_rows(rows))
        for column_name in self.required_columns:
            if column_name in self.aligns:
                table.align[column_name] = self.aligns.get(column_name)
            else:
                table.align[column_name] = 'c'
        return table.get_string()


class HTableProcessor(Processor):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_render_unit('table', TableRender)
        self.headers = {}
        self.aligns = {}

    def post_init(self):
        """TODO"""
        self._post_init = True
        self.units['format'].required_columns = self.column_names
        self.units['table'].required_columns = self.column_names
        self.units['table'].headers = self.headers
        self.units['table'].aligns = self.aligns


class VTableProcessor(Processor):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._maxlengthkey = 0
        self.headers = {}
        self._attrs += ["headers"]

    def get_headers(self):
        column_names = self.collector.required_columns
        for column_name in column_names:
            if column_name in self.headers:
                yield self.headers.get(column_name)
            else:
                yield column_name

    def get_string(self):
        """TODO"""
        max_length_line = 0
        records = []
        for row in self.get_raw():
            record = []
            for column_name in self.column_names:
                try:
                    slength = str(self._maxlengthkey)
                    t_format = "{key:" + slength + "s} | {value:s}"
                    dataa = None
                    column_data = row.get(column_name)
                    column_header = self.headers.get(column_name, column_name)
                    if isinstance(column_data, str):
                        dataa = {"key": column_header, "value": column_data}
                    else:
                        column_data_str = str(column_data)
                        dataa = {
                            "key": column_header,
                            "value": column_data_str
                        }
                    t_record = t_format.format(**dataa)
                    record.append(t_record)
                    max_length_line = max(max_length_line, len(t_record))
                except UnicodeEncodeError as ex:
                    self.log.error("UnicodeEncodeError: %s", ex)
                    dataa = {
                        "key": column_header,
                        "value": "UnicodeEncodeError"
                    }
                    t_record = str(t_format).format(**dataa)
                    record.append(t_record)
            records.append("\n".join(record))
        out = []
        cptline = 0
        for record in records:
            cptline += 1
            header = "-[ RECORD " + str(cptline) + " ]-"
            # pylint: disable=unused-variable
            range_limit = max_length_line - len(header)
            header += "".join(["-" for i in range(range_limit)])
            out.append(header)
            out.append(record)
        return "\n".join(out)


class JsonProcessor(Processor):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_json = False
        self._attrs += ["raw_json"]
        self.add_render_unit('json', CellToJsonUnit)

    def post_init(self):
        """TODO"""
        self._post_init = True
        if 'format' in self.units:
            self.units['format'].required_columns = self.column_names
        self.units['json'].required_columns = self.column_names

    def get_string(self):
        """TODO"""
        records = []
        for row in self.get_raw():
            record = {}
            for k in self.column_names:
                if self.raw_json:
                    record[k] = row.get(k).value
                else:
                    record[k] = str(row.get(k))
            records.append(record)
        return json.dumps(records, sort_keys=True, indent=2)


class CsvProcessor(Processor):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_headers = True
        self._attrs += ["csv_headers"]

    def get_string(self):
        """TODO"""
        records = []
        if self.csv_headers:
            records.append(";".join(self.column_names))
        for row in self.get_raw():
            record = []
            for k in self.column_names:
                data = row.get(k)
                if isinstance(data, str):
                    record.append(data)
                else:
                    data_str = str(data)
                    record.append(data_str)
            records.append(";".join(record))
        return "\n".join(records)


class CountProcessor(Processor):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cli_mode = False
        self.messages = {
            "count_elt": "Ressources found: {count}"
        }
        self._attrs += ["cli_mode"]

    def get_string(self):
        """TODO"""
        count = len(self.get_raw())
        if self.cli_mode:
            return str(count)
        msg = self.messages['count_elt'].format(count=count)
        self.log.debug(msg)
        return msg
