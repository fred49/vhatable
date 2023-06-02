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
from argparse import Namespace
from collections import OrderedDict


from .corev2 import HTableProcessor


class TableFactory:
    """TODO"""

    def __init__(self):
        """TODO"""
        classname = self.__class__.__name__
        self.log = logging.getLogger('vhatable.' + classname)
        self._action_classes = OrderedDict()
        self._custom_cells = {}
        self._filters = []
        self._horizontal_clazz = HTableProcessor
        self._vertical_clazz = HTableProcessor
        self._pre_render_classes = []

    @property
    def horizontal_clazz(self):
        """TODO"""
        return self._horizontal_clazz

    @horizontal_clazz.setter
    def horizontal_clazz(self, horizontal_clazz):
        """TODO"""
        self._horizontal_clazz = horizontal_clazz

    def set_custom_cell(self, column, builder):
        """Add specific cell class to format a column."""
        self._custom_cells[column] = builder

    def set_action(self, flag, clazz):
        """Add some custom action class trigger by a flag."""
        self._action_classes[flag] = clazz

    def add_filter_cond(self, condition, *filters):
        """Add some filters only if condition is true"""
        if condition:
            for filterr in filters:
                self._filters.append(filterr)

    def add_filters(self, *filters):
        """Add some filters."""
        for filterr in filters:
            self._filters.append(filterr)
        return self

    def add_pre_render_class(self, clazz):
        """TODO"""
        self._pre_render_classes.append(clazz)

    def build(self, args=Namespace()):
        vertical = getattr(args, "vertical", False)
        debug = getattr(args, "debug", False)
        table = None
        if vertical:
            table = self._vertical_clazz(debug=debug)
        else:
            table = self._horizontal_clazz(debug=debug)
            # table.padding_width = 1
        for clazz in self._pre_render_classes:
            table.add_pre_render_class(clazz)

        table.filter.add(*self._filters)
        for column, builder in self._custom_cells.items():
            table.format.cfa.custom_cells[column] = builder

        table.format.cfa.vertical = vertical
        # table.cfa.debug = self.debug

        table.setup(args)
        return table
