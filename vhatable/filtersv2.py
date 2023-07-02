#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains only filters, they are design to be apply to a row
of a Vertical or Horizotal table."""


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
# Copyright 2023 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#

from datetime import datetime
from datetime import timedelta

from .filters import Equals
from .filters import Filter


# Equal | Partial | Greater | Older | Newer
# Single value | Multiple Value
# And | Or


class EqualMultipleOr(Equals):
    """
    Get the current property into the current row, and test equality with any
    provided values."""


class PartialMultipleAnd(Filter):
    """Get the current property into the current row, and match the result with
     ALL values of the list"""

    def __init__(self, prop, values):
        super().__init__(prop, values)
        if self.is_enable():
            if not isinstance(values, list):
                raise ValueError("input values should be a list")
            self.log.debug("values: %s", self.values)

    def __str__(self):
        return "PartialMultipleAnd: " + str(self.values)

    def __call__(self, row):
        if not self.is_enable():
            return True
        # comp must be a cell
        comp = str(self.get_val(row))
        lower_comp = comp.lower()
        for val in self.values:
            lower_val = val.lower()
            if val == lower_val:
                if lower_val not in lower_comp:
                    return False
            else:
                if val not in comp:
                    return False
        return True


class OlderThanFilter(Filter):
    """Get the  property into the row and return only row older than N days.
    This filter can only be used with DateCells, inner value should be a Long.
    """

    def __init__(self, prop, nb_days):
        super().__init__(prop, nb_days)
        if self.is_enable():
            date = self._get_today() - timedelta(days=nb_days)
            self.timestamp_to_compare = date.timestamp()

    def _get_today(self):
        return datetime.today()

    def __call__(self, row):
        if not self.is_enable():
            return True
        cell = self.get_val(row)
        value = cell.value
        if cell.millisecond:
            value = value / 1000
        # self.log.debug("cell: %s, %s", cell, value)
        if self.timestamp_to_compare > value:
            return True
        return False


class NewerThanFilter(Filter):
    """Get the property into the row and return only row newer than N days.
    This filter can only be used with DateCells, inner value should be a Long.
    """

    def __init__(self, prop, nb_days):
        super().__init__(prop, nb_days)
        if self.is_enable():
            date = self._get_today() - timedelta(days=nb_days)
            self.timestamp_to_compare = date.timestamp()

    def _get_today(self):
        return datetime.today()

    def __call__(self, row):
        if not self.is_enable():
            return True
        cell = self.get_val(row)
        value = cell.value
        if cell.millisecond:
            value = value / 1000
        # self.log.debug("cell: %s, %s", cell, value)
        if self.timestamp_to_compare < value:
            return True
        return False
