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
from datetime import datetime

from .corev2 import AbstractProcessor
from .corev2 import Time
from .units import FormattingUnit
from .units import FilteringUnit
from .units import SortingUnit
from .units import SlicingUnit
from .units import TableRender
from .units import CellToJsonUnit


class Processor(AbstractProcessor):
    """TODO"""

    def __init__(self, *args, api=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api
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

    def __init__(self, *args, messages=None, **kwargs):
        super().__init__(*args, messages=messages, **kwargs)
        self.cli_mode = False
        self.messages["count_elt"] = "Ressources found: {count}"
        self._attrs += ["cli_mode"]
        if messages:
            self.messages.update(messages)

    def get_string(self):
        """TODO"""
        count = len(self.get_raw())
        if self.cli_mode:
            return str(count)
        msg = self.messages['count_elt'].format(count=count)
        self.log.debug(msg)
        return msg


class ProcessorBuilder:
    """This builder is design to be used by the factory to create a processor.
    It will create the processor and passing some default arguments to the
    constructor. It could be extended to provide some extra parameters to a
    specific processor.
    """

    def __init__(self, debug=0, rows=None, column_names=None,
                 autokeys=True, messages=None, api=None):
        # pylint: disable=too-many-arguments
        self.debug = debug
        self.rows = rows
        self.autokeys = autokeys
        self.column_names = column_names
        self.messages = messages
        self.api = api

    def __call__(self, clazz):
        processor = clazz(
                debug=self.debug,
                autokeys=self.autokeys,
                column_names=self.column_names,
                messages=self.messages,
                api=self.api,
                rows=self.rows)
        return self._post_create_hook(processor)

    def _post_create_hook(self, processor):
        return processor

    def use_api(self, api):
        """trying to get automatically data and column names from api."""
        if hasattr(api, "column_names"):
            self.column_names = api.column_names()
        if hasattr(api, "list"):
            self.rows = api.list()
        return self


class DeleteProcessor(Processor):
    """TODO"""

    def __init__(self, *args,  messages=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_transform_unit(
                'json', CellToJsonUnit, dump=False, raw=True)
        self.messages = {
            "deleted": (
                "{_position}/{_count}: "
                "The ressource '{name}' ({uuid}) was deleted. ({_time}s)"
            )
        }
        if messages:
            self.messages.update(messages)

    def post_init(self):
        """TODO"""
        super().post_init()
        self.units['json'].required_columns = self.column_names

    @Time('vhatable.corev2.run')
    def run(self):
        """TODO"""
        print(">>>>>>")
        default_context = {
            "name": None,
            "uuid": None,
            "_time": 0,
            "_position": 0,
            "_count": len(self.get_raw())
        }
        position = 0
        for row in self.get_raw():
            position += 1
            before = datetime.now()
            self.api.delete(row)
            after = datetime.now()
            context = {
                **default_context,
                **row,
                "_position": position,
                "_time": after - before
            }
            msg = self.messages['deleted'].format(**context)
            self.log.debug(msg)
            print(msg)
        print()
        return True


class ProcessorFactory:
    """class in charge of creating to proper processor according input args.
    This class is also in charge of proviging all processor's config.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, with_delete_proc=True):
        """TODO"""
        classname = self.__class__.__name__
        self.log = logging.getLogger('vhatable.' + classname)

        self.cfg = OrderedDict()
        builder = ProcessorBuilder()
        self.cfg['count'] = self._create_cfg(builder, CountProcessor)
        self.cfg['cli_mode'] = self._create_cfg(builder, CountProcessor)
        self.cfg['vertical'] = self._create_cfg(builder, VTableProcessor)
        self.cfg['csv'] = self._create_cfg(builder, CsvProcessor)
        self.cfg['json'] = self._create_cfg(builder, JsonProcessor)
        self.cfg['horizontal'] = self._create_cfg(builder, HTableProcessor)
        if with_delete_proc:
            self.cfg['delete'] = self._create_cfg(builder, DeleteProcessor)
        self.default_proc = "horizontal"

        self._custom_cells = {}
        self._header_cells = {}
        self._align_cells = {}
        self._filters = []
        self._pre_render_classes = []

    def _create_cfg(self, builder, clazz):
        return {
            "builder": builder,
            "clazz": clazz
        }

    def set_default_processor_builder(self, builder):
        """Set a default processor builder for all processors"""
        if not isinstance(builder, ProcessorBuilder):
            msg = "1st argument (builder) must be an ProcessorBuilder instance"
            raise ValueError(msg)
        for proc_cfg in self.cfg.values():
            proc_cfg['builder'] = builder

    def add_processor(self, flag, builder, processor_clazz):
        """Add some custom action class trigger by a flag."""
        if not isinstance(builder, ProcessorBuilder):
            msg = "2nd argument (builder) must be an ProcessorBuilder instance"
            raise ValueError(msg)
        self.cfg[flag] = self._create_cfg(builder, processor_clazz)

    def set_header_cell(self, column_name, header_value):
        """set a header value for an existing displayed column."""
        self._header_cells[column_name] = header_value

    def set_align_cell(self, column_name, align_value):
        """set a align value for an existing displayed column."""
        self._align_cells[column_name] = align_value

    def set_custom_cell(self, column, builder):
        """Add specific cell class to format a column."""
        self._custom_cells[column] = builder

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

    def _get_processor(self, args):
        """Retrieve the proper builder from the config to build the processor.
        """
        builder = None
        clazz = None
        for flag in self.cfg.keys():
            if getattr(args, flag, False):
                builder, clazz = self.cfg.get(flag).values()
                break
        if builder is None:
            builder, clazz = self.cfg.get(self.default_proc).values()
        self.log.debug("builder: %s", builder)
        self.log.debug("clazz: %s", clazz)
        processor = builder(clazz)
        self.log.debug("processor: %s", processor)
        return processor

    def create(self, args=Namespace(), default_builder=None):
        """create a new processor and do the setup."""
        if default_builder:
            self.set_default_processor_builder(default_builder)
        self.log.debug("self.cfg: %s", self.cfg)
        processor = self._get_processor(args)

        msg = "warn:filter unit is not provided/added to the current processor"
        if hasattr(processor, 'filter'):
            processor.filter.add(*self._filters)
        else:
            self.log.debug(msg)

        msg = "format unit is not provided/added to the current processor"
        if hasattr(processor, 'format'):
            for cell_name, cbuilder in self._custom_cells.items():
                processor.format.cfa.custom_cells[cell_name] = cbuilder
        else:
            self.log.debug(msg)

        msg = "processor.headers does not exist in the current processor"
        if hasattr(processor, 'headers'):
            for column_name, header_value in self._header_cells.items():
                processor.headers[column_name] = header_value
        else:
            self.log.debug(msg)

        msg = "processor.aligns does not exist in the current processor"
        if hasattr(processor, 'aligns'):
            for column_name, align_value in self._align_cells.items():
                processor.aligns[column_name] = align_value
        else:
            self.log.debug(msg)

        processor.setup(args)
        return processor
