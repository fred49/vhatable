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
from functools import wraps


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


class AutoTime:
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, label="execution time: {time:.15f}"):
        self.enabled = False
        self.label = label

    def __call__(self, original_func):
        @wraps(original_func)
        def time_wrapper(*args, **kwargs):
            logger_name = args[0].__class__.__name__
            logger_name += "." + original_func.__name__
            log = logging.getLogger(logger_name)
            log.debug("args: %s", args)
            log.debug("kwargs: %s", kwargs)
            start = time.time()
            res = original_func(*args, **kwargs)
            end = time.time()
            if len(args) > 0:
                first_arg = args[0]
                self.enabled = getattr(first_arg, "verbose", self.enabled)
            diff = end - start
            msg = self.label.format(time=diff)
            log.debug(msg)
            if self.enabled:
                print(msg)
            return res
        return time_wrapper


class Unit:
    """TODO"""

    def __init__(self, typ="transform",  debug=0, identifier=None):
        self.log = logging.getLogger(__name__)
        self._debug = debug
        self._verbose = False
        self.identifier = identifier
        self._attrs = []
        self._gattrs = ["debug", "verbose"]
        self._attrs_ro = []
        self.typ = typ

    @property
    def debug(self):
        """TODO"""
        return self._debug

    @debug.setter
    def debug(self, debug):
        """TODO"""
        self._debug = debug

    @property
    def verbose(self):
        """TODO"""
        return self._verbose

    @verbose.setter
    def verbose(self, verbose):
        """TODO"""
        self._verbose = verbose

    def setup(self, from_args):
        """TODO"""
        for attr in self._gattrs:
            if hasattr(from_args, attr):
                setattr(self, attr, getattr(from_args, attr))
            self.log.debug("setup:gattr: %s : %s", attr, getattr(self, attr))
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
        for attr in self._gattrs:
            attr_val = getattr(self, attr)
            rows.append(f" - global: {attr}: {attr_val}")
        for attr in self._attrs:
            attr_val = getattr(self, attr)
            rows.append(f" - {prefix}{attr}: {attr_val}")
        for attr in self._attrs_ro:
            attr_val = getattr(self, attr)
            rows.append(f" - readonly: {prefix}{attr}: {attr_val}")
        rows.append("")
        return "\n".join(rows)

    def __call__(self, rows):
        raise NotImplementedError()


class AbstractProcessor:
    """TODO"""
    # pylint: disable=too-many-instance-attributes

    def __init__(self, debug=0, verbose=False, rows=None, column_names=None,
                 autokeys=True, messages=None, identifier=None):
        # pylint: disable=too-many-arguments
        self._attrs = ["debug", "verbose", "column_names"]
        self._attrs_ro = ["identifier", "messages"]
        classname = str(self.__class__.__name__.lower())
        self.log = logging.getLogger('vhatable.' + classname)
        self.identifier = identifier
        self.units = OrderedDict()
        self.column_names = []
        self._rows = []
        self._raw_cache = None
        self._post_init = False
        self.messages = {}
        self.messages[self.identifier] = {}
        self.debug = debug
        self.verbose = verbose
        if rows:
            self._rows = rows
        if column_names:
            self.column_names = column_names
        elif autokeys:
            if rows and len(rows) >= 1:
                self.column_names = rows[0].keys()
        self._update_messages(messages)

    def _update_messages(self, messages):
        if messages:
            if self.identifier in messages:
                messages = messages[self.identifier]
                self.messages[self.identifier].update(messages)

    def _format_messages(self, key, data):
        return self.messages[self.identifier][key].format(**data)

    def add_unit(self, unit):
        """TODO"""
        self.units[unit.identifier] = unit

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
        for attr in self._attrs_ro:
            attr_val = getattr(self, attr)
            rows.append(f" - readonly: {attr}: {attr_val}")
        rows.append("")
        for unit in self.units.values():
            rows.append(str(unit))
        return "\n".join(rows)

    def pre_get_raw_hook(self):
        """When get_raw method is called, this method is called just before
        doing anything. It could be use full to run some extra configuration
        steps.
        """

    def get_raw(self):
        """TODO"""
        if self._raw_cache is not None:
            if self.debug >= 2:
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
                self.log.debug("unit:transform: %s", unit)
                self.log.debug("unit:transform:begin: %s", unit.__class__.__name__)
                pipeline = unit(pipeline)
                self.log.debug("unit:transform:end  : %s", unit.__class__.__name__)
        self._raw_cache = list(pipeline)
        if self.debug >= 2:
            self.log.debug("pipeline rows: %s", self._raw_cache)
        return self._raw_cache

    def load(self, rows):
        """TODO"""
        self._rows = rows
        return self

    def setup(self, from_args):
        """TODO"""
        self.post_init()
        for attr in self._attrs:
            if hasattr(from_args, attr):
                setattr(self, attr, getattr(from_args, attr))
            self.log.debug("setup:attr: %s : %s", attr, getattr(self, attr))
        for unit in self.units.values():
            unit.setup(from_args)
        return self

    @Time('vhatable.corev2.run')
    def run(self):
        """TODO"""
        for row in self.get_raw():
            print(row)
        return True
