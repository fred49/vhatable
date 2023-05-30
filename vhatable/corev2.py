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


import logging

from collections import OrderedDict
from tabulate import tabulate

from .cellv2 import CellBuilderFactory
from .core import Time as CTime


class Time(CTime):
    """TODO"""

    def __init__(self,
                 logger_name,
                 label="execution time: %(time)s"):
        super().__init__(logger_name, label)


class Module:
    """TODO"""
    __dict__ = ["debug"]

    def __init__(self, debug=0):
        self.log = logging.getLogger(__name__)
        self._debug = debug

    @property
    def debug(self):
        """TODO"""
        return self._debug

    @debug.setter
    def debug(self, debug):
        """TODO"""
        self._debug = debug

    def setup_from_args(self, args):
        """TODO"""
        for attr in self.__dict__:
            if hasattr(args, attr):
                setattr(self, attr, getattr(args, attr))
        return self


class FilteringModule(Module):
    """TODO"""
    __dict__ = ["debug"]

    def __init__(self, debug=0):
        super().__init__(debug=debug)
        self._filters = []
        self._rows = []

    def add(self, *filters):
        """Add some filters."""
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


class SortingModule(Module):
    """TODO"""
    __dict__ = ["debug", "reverse", "sort_by"]

    def __init__(self, debug=0):
        super().__init__(debug=debug)
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


class FormattingModule(Module):
    """TODO"""
    __dict__ = ["debug", "no_cell", "vertical", "extended"]

    def __init__(self, debug=0):
        super().__init__(debug=debug)
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
            yield row_full


class SlicingModule(Module):
    """TODO"""
    __dict__ = ["debug", "start", "end", "limit"]

    def __init__(self, debug=0):
        super().__init__(debug=debug)
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


class CollectorModule(Module):
    """TODO"""
    __dict__ = ["debug"]

    def __init__(self, debug=0):
        super().__init__(debug=debug)
        self.required_columns = []

    def __call__(self, rows):
        for row in rows:
            newrow = []
            for column_name in self.required_columns:
                newrow.append(row.get(column_name))
            self.log.debug("newrow: %s", newrow)
            if newrow:
                yield newrow


class AbstractTable:
    """TODO"""

    log = None
    csv = False
    json = False
    debug = 0
    verbose = False

    vertical = False
    extended = False
    raw_display = False
    cli_mode = False
    args = None
    cli = None
    endpoint = None
    _pre_render_classes = []

    def add_pre_render_class(self, clazz):
        """TODO"""
        self._pre_render_classes.append(clazz)

    def get_raw(self):
        """TODO"""
        raise NotImplementedError()

    def get_json(self):
        """TODO"""
        raise NotImplementedError()

    def get_csv(self):
        """TODO"""
        raise NotImplementedError()

    def get_string(self):
        """TODO"""
        raise NotImplementedError()

    def load(self, rows):
        """TODO"""
        raise NotImplementedError()

    def _display_nb_elts(self):
        """TODO"""
        raise NotImplementedError()

    def _pre_render(self):
        """Trigger some classes before rendering filtered data."""
        for clazz in self._pre_render_classes:
            self.log.debug(clazz)
            clazz(self.args, self.cli, self.endpoint, self.get_raw())

    @Time('vhatable.corev2.render', label='render time: %(time)s')
    def render(self):
        """TODO"""
        if self.json:
            print(self.get_json())
            return True
        if self.csv:
            print(self.get_csv())
            return True
        self._pre_render()
        print(self.get_string())
        self._display_nb_elts()
        return True


class BaseTable(AbstractTable):
    """TODO"""

    def __init__(self, debug=0):
        classname = str(self.__class__.__name__.lower())
        self.log = logging.getLogger('vhatable.' + classname)
        self.modules = OrderedDict()
        self.modules['format'] = FormattingModule(debug=debug)
        self.modules['filter'] = FilteringModule(debug=debug)
        self.modules['sort'] = SortingModule(debug=debug)
        self.modules['slicing'] = SlicingModule(debug=debug)
        self.modules['collector'] = CollectorModule(debug=debug)
        self._column_names = []
        self._rows = []
        self._raw_cache = None
        self.showindex = True
        self.tablefmt = 'grid'
        self.messages = {
            "count_elt": "\nRessources found: {count}"
        }

    def __getattr__(self, attr):
        if attr in self.modules:
            return self.modules[attr]
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
        self.modules['format'].required_columns = column_names
        self.modules['collector'].required_columns = column_names

    def load(self, rows):
        """TODO"""
        self._rows = rows
        return self

    def get_raw(self):
        """TODO"""
        if self._raw_cache is not None:
            return self._raw_cache
        pipeline = self._rows
        for module in self.modules.values():
            pipeline = module(pipeline)
        self._raw_cache = list(pipeline)
        return self._raw_cache

    def get_string(self):
        """TODO"""
        return tabulate(
                self.get_raw(),
                showindex=self.showindex,
                tablefmt=self.tablefmt,
                stralign='center',
                headers=self._column_names)

    def get_json(self):
        """TODO"""
        raise NotImplementedError()

    def get_csv(self):
        """TODO"""
        raise NotImplementedError()

    def _display_nb_elts(self):
        """TODO"""
        if self.verbose:
            msg = self.messages['count_elt'].format(
                    count=len(self.get_raw())
            )
            self.log.debug(msg)
            print(msg)
        return True
