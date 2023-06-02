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
import logging

from collections import OrderedDict
from tabulate import tabulate
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
    __dict__ = ["debug"]

    def __init__(self, debug=0, identifier=None):
        self.log = logging.getLogger(__name__)
        self._debug = debug
        self.identifier = identifier

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
        for attr in self.__dict__:
            if self.identifier:
                attr_with_prefix = self.identifier + "_" + attr
                if hasattr(from_args, attr_with_prefix):
                    setattr(self, attr, getattr(from_args, attr_with_prefix))
            else:
                if hasattr(from_args, attr):
                    setattr(self, attr, getattr(from_args, attr))
        return self


class FilteringUnit(Unit):
    """TODO"""
    __dict__ = ["debug"]

    def __init__(self, debug=0, identifier=None):
        super().__init__(debug=debug, identifier=identifier)
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
    __dict__ = ["debug", "reverse", "sort_by"]

    def __init__(self, debug=0, identifier=None):
        super().__init__(debug=debug, identifier=identifier)
        self.reverse = False
        self.sort_by = None

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
    __dict__ = ["debug", "no_cell", "vertical", "extended"]

    def __init__(self, debug=0, identifier=None):
        super().__init__(debug=debug, identifier=identifier)
        self.no_cell = False
        self.vertical = False
        self.extended = False
        self.raw_display = False
        self.cfa = CellBuilderFactory()
        self.cfa.debug = debug
        self.required_columns = []
        self.compute_column_for_each_row = False
        self._columns = []

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
    __dict__ = ["debug", "start", "end", "limit"]

    def __init__(self, debug=0, identifier=None):
        super().__init__(debug=debug, identifier=identifier)
        self.limit = 0
        self.start = 0
        self.end = 0

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
    __dict__ = ["debug"]

    def __init__(self, debug=0, identifier=None):
        super().__init__(debug=debug, identifier=identifier)
        self.required_columns = []

    def __call__(self, rows):
        for row in rows:
            newrow = []
            for column_name in self.required_columns:
                newrow.append(row.get(column_name))
            self.log.debug("newrow: %s", newrow)
            if newrow:
                yield newrow


class AbstractProcessor:
    """TODO"""

    def __init__(self, debug=0):
        classname = str(self.__class__.__name__.lower())
        self.log = logging.getLogger('vhatable.' + classname)
        self.units = OrderedDict()
        self._column_names = []
        self._rows = []
        self._raw_cache = None
        self.messages = {}
        self.debug = debug
        self.verbose = False

    def add_unit(self, identifier, unit):
        """TODO"""
        self.units[identifier] = unit(identifier=identifier)

    def __getattr__(self, attr):
        if attr in self.units:
            return self.units[attr]
        classname = self.__class__.__name__
        raise AttributeError(f"'{classname}' object has no attribute '{attr}'")

    @property
    def column_names(self):
        """TODO"""
        return self._column_names

    @column_names.setter
    def column_names(self, column_names):
        """TODO"""
        self._column_names = column_names

    def get_raw(self):
        """TODO"""
        self.log.debug("Units: %s", self.units)
        self.log.debug("Rows: %s", self._rows)
        if self._raw_cache is not None:
            self.log.debug("cached rows: %s", self._raw_cache)
            return self._raw_cache
        pipeline = self._rows
        for unit in self.units.values():
            self.log.debug("unit: %s", unit)
            pipeline = unit(pipeline)
        self._raw_cache = list(pipeline)
        self.log.debug("pipeline rows: %s", self._raw_cache)
        return self._raw_cache

    def get_string(self):
        """TODO"""
        raise NotImplementedError()

    def load(self, rows):
        """TODO"""
        self._rows = rows
        return self

    def setup(self, from_args):
        """TODO"""
        for unit in self.units.values():
            unit.setup(from_args)
        return self

    @Time('vhatable.corev2.run')
    def run(self):
        """TODO"""
        print(self.get_string())
        return True


class Processor(AbstractProcessor):
    """TODO"""

    def __init__(self, debug=0):
        super().__init__(debug=debug)
        self.add_unit('format', FormattingUnit)
        self.add_unit('filter', FilteringUnit)
        self.add_unit('sort', SortingUnit)
        self.add_unit('slice', SlicingUnit)

    @property
    def column_names(self):
        """TODO"""
        return self._column_names

    @column_names.setter
    def column_names(self, column_names):
        """TODO"""
        self._column_names = column_names
        self.units['format'].required_columns = column_names

    def get_string(self):
        """TODO"""
        return self.get_raw()


class HTableProcessor(Processor):
    """TODO"""

    def __init__(self, debug=0):
        super().__init__(debug=debug)
        self.add_unit('collector', CollectorUnit)
        self.showindex = True
        self.tablefmt = 'grid'

    @property
    def column_names(self):
        """TODO"""
        return self._column_names

    @column_names.setter
    def column_names(self, column_names):
        """TODO"""
        self._column_names = column_names
        self.units['format'].required_columns = column_names
        self.units['collector'].required_columns = column_names

    def get_string(self):
        """TODO"""
        return tabulate(
                self.get_raw(),
                showindex=self.showindex,
                tablefmt=self.tablefmt,
                stralign='center',
                headers=self._column_names)


class VTableProcessor(Processor):
    """TODO"""

    def __init__(self, debug=0):
        super().__init__(debug=debug)


class JsonProcessor(Processor):
    """TODO"""

    def __init__(self, debug=0):
        super().__init__(debug=debug)


class CsvProcessor(Processor):
    """TODO"""

    def __init__(self, debug=0):
        super().__init__(debug=debug)
        self.csv_headers = True

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

    def __init__(self, debug=0):
        super().__init__(debug=debug)
        self.cli_mode = False
        self.messages = {
            "count_elt": "Ressources found: {count}"
        }

    def get_string(self):
        """TODO"""
        count = len(self.get_raw())
        if self.cli_mode:
            return str(count)
        msg = self.messages['count_elt'].format(count=count)
        self.log.debug(msg)
        return msg
