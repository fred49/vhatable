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


from .corev2 import AbstractProcessor
from .corev2 import FormattingUnit
from .corev2 import FilteringUnit
from .corev2 import SortingUnit
from .corev2 import SlicingUnit
from .corev2 import TableRender
from .corev2 import CellToJsonUnit


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


class HTableProcessor(Processor):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_render_unit('table', TableRender)
        self.headers = {}
        self.aligns = {}

    def post_init(self):
        """TODO"""
        super().post_init()
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
        """for each column, use column name or a custom name as table header"""
        column_names = self.collector.required_columns
        for column_name in column_names:
            if column_name in self.headers:
                yield self.headers.get(column_name)
            else:
                yield column_name

    def get_string(self):
        """TODO"""
        # pylint: disable=too-many-locals
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
        self.add_render_unit('json', CellToJsonUnit)

    def post_init(self):
        """TODO"""
        super().post_init()
        self.units['json'].required_columns = self.column_names


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
