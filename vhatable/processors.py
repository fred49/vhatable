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


import copy
import logging
from argparse import Namespace
from collections import OrderedDict
from datetime import datetime

from .cellv2 import CellBuilder
from .corev2 import AbstractProcessor
from .corev2 import Time
from .units import FormattingUnit
from .units import FilteringUnit
from .units import SortingUnit
from .units import SlicingUnit
from .units import TableRender
from .units import HeaderRender
from .units import FooterRender
from .units import CellToJsonUnit
from .units import UpdateRowsUnit


class API:
    """TODO"""

    def __init__(self):
        self.data = []

    def list(self):
        """TODO"""
        return self.data

    def column_names(self):
        """TODO"""
        return []

    def get(self, row_id):
        """TODO"""
        # pylint: disable=unused-argument
        classname = self.__class__.__name__
        raise NotImplementedError(
            f"class {classname} has not implemented get method")

    def delete(self, row):
        """TODO"""
        # pylint: disable=unused-argument
        # expected: return True|False, update_row
        classname = self.__class__.__name__
        raise NotImplementedError(
            f"class {classname} has not implemented delete method")

    def update(self, row):
        """TODO"""
        # pylint: disable=unused-argument
        classname = self.__class__.__name__
        # expected: return True|False, update_row
        raise NotImplementedError(
            f"class {classname} has not implemented update method")


class Processor(AbstractProcessor):
    """TODO"""

    def __init__(self, *args, dry_run=False, api=API(), **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api
        self.dry_run = dry_run
        self.add_unit(FormattingUnit(identifier='format'))
        self.add_unit(FilteringUnit(identifier='filter'))
        self.add_unit(SortingUnit(identifier='sort'))
        self.add_unit(SlicingUnit(identifier='slice'))
        self._attrs += ["dry_run"]

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

    def get_string(self):
        """TODO"""
        result = []
        for unit in self.units.values():
            if unit.typ == "render":
                if self.debug >= 2:
                    self.log.debug("unit:render: %s", unit)
                string = unit(self.get_raw())
                if string:
                    result.append(string)
        return "\n".join(result)

    @Time('vhatable.corev2.run')
    def run(self):
        """TODO"""
        print(self.get_string())
        return True


class HTableProcessor(Processor):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_unit(HeaderRender())
        self.add_unit(TableRender(identifier='table', typ="render"))
        self.add_unit(FooterRender())
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
        self._maxlengthkey = 20
        self.headers = {}
        self.columns_to_show = []
        self._attrs += ["headers", "columns_to_show"]

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
        if not self.columns_to_show:
            self.columns_to_show = list(self.column_names)
        max_length_line = 0
        records = []
        for row in self.get_raw():
            record = []
            for column_name in self.columns_to_show:
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
        self.add_unit(CellToJsonUnit(identifier='json', typ="render"))

    def post_init(self):
        """TODO"""
        super().post_init()
        self.units['json'].required_columns = self.column_names


class CsvProcessor(Processor):
    """TODO"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_header = True
        self.columns_to_show = []
        self._attrs += ["csv_header", "columns_to_show"]

    def get_string(self):
        """TODO"""
        records = []
        if not self.columns_to_show:
            self.columns_to_show = list(self.column_names)
        if self.csv_header:
            records.append(";".join(self.columns_to_show))
        for row in self.get_raw():
            record = []
            for k in self.columns_to_show:
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
        self.messages[self.identifier]["count_elt"] = "Ressources found: {count}"
        self._attrs += ["cli_mode"]
        self._update_messages(messages)

    def get_string(self):
        """TODO"""
        count = len(self.get_raw())
        if self.cli_mode:
            return str(count)
        msg = self.messages[self.identifier]["count_elt"].format(count=count)
        self.log.debug(msg)
        return msg


class ProcessorBuilder:
    """This builder is design to be used by the factory to create a processor.
    It will create the processor and passing some default arguments to the
    constructor. It could be extended to provide some extra parameters to a
    specific processor.
    """

    def __init__(self, debug=0, rows=None, column_names=None,
                 autokeys=True, messages=None, api=API(), units=None,
                 autoload=False, extra_args=None):
        """A ProcessorBuilder is in charge of creating processors.
        it is used by ProcessorFactory.

          @type debug: int
          @param debug: Debug log level
          @type rows: list of dict values OR a callable (lazyness)
          @param rows: Optional; list of rows to be displayed
          @type column_names: list of str OR a callable (lazyness)
          @param column_names: Optional; a list of column names
          @type autokeys: bool
          @param rows: Optional; Trying to guest colun names from input rows
          @type messages: dict
          @param messages: Optional; a dict of messages to overide default ones
          @type api: api instance
          @param api: Optional; Used by delete processor. See API class for
          more details. AbstractApi is used by default
          @type units: list of Units
          @param units: Optional; a list of unit to add to the processor
          @type autoload: bool
          @param autoload: Optional; load rows and column names from api. Default: False
          @rtype: ProcessorBuilder
          @returns builder: instance
          """
        self.debug = debug
        self.rows = rows
        self.units = units or []
        self.autokeys = autokeys
        self.column_names = column_names
        self.messages = messages
        self.api = api
        self.extra_args = {}
        if extra_args:
            self.extra_args = extra_args
        self.autoload = autoload

    def __call__(self, identifier, clazz):
        rows = self.rows
        column_names = self.column_names
        if self.autoload:
            rows = self.api.list()
            column_names = self.api.column_names()
        else:
            if callable(rows):
                rows = rows()
            if callable(column_names):
                column_names = column_names()
        processor = clazz(
                rows=rows,
                column_names=column_names,
                debug=self.debug,
                autokeys=self.autokeys,
                messages=self.messages,
                api=self.api,
                identifier=identifier,
                **self.extra_args,
        )
        for unit in self.units:
            processor.add_unit(unit)
        return self._post_create_hook(processor)

    def _post_create_hook(self, processor):
        return processor


class DoProcessor(Processor):
    """TODO"""

    def __init__(self, *args,  messages=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages[self.identifier] = {
            "nothing_to_do": "Nothing to do.",
            "done": (
                "{prefix}{_position}/{_count}: "
                "The ressource '{name}' ({uuid}) was done. ({_time}s)"
            ),
            "done_failure": (
                "{prefix}{_position}/{_count}: Failure "
                "The ressource '{name}' ({uuid}) was not done. ({_time}s)"
            )
        }
        self._update_messages(messages)

    def _do_row(self, row, context):
        # pylint: disable=unused-argument
        if self.dry_run:
            return True, row
        raise NotImplementedError("_do_row is not implemented.")

    @Time('vhatable.do.run')
    def run(self):
        """TODO"""
        default_context = {
            "name": None,
            "uuid": None,
            "prefix": "DRY-RUN: " if self.dry_run else "",
            "_time": 0,
            "_position": 0,
            "_count": len(self.get_raw())
        }
        position = 0
        final_result = True
        if default_context['_count'] == 0:
            msg = self._format_messages('nothing_to_do', {})
            self.log.debug(msg)
            print(msg)
        for row in self.get_raw():
            position += 1
            context = {
                **default_context,
                "_position": position,
            }
            self.log.debug("row keys: %s", row.keys())
            before = datetime.now()
            result, do_row = self._do_row(row, context)
            after = datetime.now()
            context['_time'] = after - before
            context.update(do_row)
            if result:
                msg = self._format_messages('done', context)
            else:
                msg = self._format_messages('done_failure', context)
                final_result = False
            self.log.debug(msg)
            print(msg)
        print()
        return final_result


class DeleteProcessor(DoProcessor):
    """TODO"""

    def __init__(self, *args,  messages=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_unit(CellToJsonUnit(
            identifier='json',
            dump=False, raw=True)
        )
        self.messages[self.identifier] = {
            "nothing_to_do": "Nothing to delete.",
            "done": (
                "{prefix}{_position}/{_count}: "
                "The ressource '{name}' ({uuid}) was deleted. ({_time}s)"
            ),
            "done_failure": (
                "{prefix}{_position}/{_count}: Failure "
                "The ressource '{name}' ({uuid}) was not deleted. ({_time}s)"
            )
        }
        self._update_messages(messages)

    def post_init(self):
        """TODO"""
        super().post_init()
        self.units['json'].required_columns = self.column_names

    def _do_row(self, row, context):
        if self.dry_run:
            return True, row
        return self.api.delete(row)


class UpdateProcessor(DoProcessor):
    """TODO"""

    def __init__(self, *args,  messages=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_unit(CellToJsonUnit(
            identifier='json', dump=False, force_raw=True))
        self.add_unit(UpdateRowsUnit())
        self.messages[self.identifier] = {
            "nothing_to_do": "Nothing to update.",
            "done": (
                "{prefix}{_position}/{_count}: "
                "The ressource '{name}' ({uuid}) was updated. ({_time}s)"
            ),
            "done_failure": (
                "{prefix}{_position}/{_count}: Failure "
                "The ressource '{name}' ({uuid}) was not updated. ({_time}s)"
            )
        }
        self._update_messages(messages)

    def post_init(self):
        """TODO"""
        super().post_init()
        self.units['json'].required_columns = self.column_names
        if not self.units['update'].updatable_columns:
            # if updatable_columns was not defined in the constructor,
            # we automatically define all columns as updatable
            self.units['update'].updatable_columns = self.column_names

    def _do_row(self, row, context):
        if self.dry_run:
            return True, row
        return self.api.update(row)


class ProcessorFactory:
    """class in charge of creating to proper processor according input args.
    This class is also in charge of proviging all processor's config.
    """

    def __init__(self, with_delete_proc=True, with_update_proc=True):
        """TODO"""
        classname = self.__class__.__name__
        self.log = logging.getLogger('vhatable.' + classname)

        self.cfg = OrderedDict()
        self.default_processor_builder_instance = ProcessorBuilder()
        self.default_processor_identifier = "horizontal"

        self.add_processor("count", CountProcessor)
        self.add_processor("vertical", VTableProcessor)
        self.add_processor("csv", CsvProcessor)
        self.add_processor("json", JsonProcessor)
        self.add_processor("horizontal", HTableProcessor)
        if with_delete_proc:
            self.add_processor("delete", DeleteProcessor)
        if with_update_proc:
            self.add_processor("update", UpdateProcessor)

        self._custom_cells = {}
        self._header_cells = {}
        self._units = {}
        self._align_cells = {}
        self._filters = []
        self._pre_render_classes = []

    def set_default_processor_builder(self, builder):
        """Set a default processor builder"""
        if not isinstance(builder, ProcessorBuilder):
            msg = "1st argument (builder) must be an ProcessorBuilder instance"
            raise ValueError(msg)
        self.default_processor_builder_instance = builder

    def set_default_processor_builder2(self, builder):
        """Set a default processor builder for all processors"""
        if not isinstance(builder, ProcessorBuilder):
            msg = "1st argument (builder) must be an ProcessorBuilder instance"
            raise ValueError(msg)
        for identifier, proc_cfg in self.cfg.items():
            builder_copy = copy.copy(builder)
            builder_copy.identifier = identifier
            proc_cfg['builder'] = builder_copy

    def add_unit(self, unit):
        """TODO"""
        self._units[unit.identifier] = unit

    def add_processor(self, identifier, processor_clazz, builder=None):
        """Add some custom action class trigger by a its identifier."""
        if builder and not isinstance(builder, ProcessorBuilder):
            msg = "Third argument (builder) must be an ProcessorBuilder instance"
            raise ValueError(msg)
        self.cfg[identifier] = {
            "builder": builder,
            "clazz": processor_clazz
        }

    def set_header_cell(self, column_name, header_value):
        """set a header value for an existing displayed column."""
        self._header_cells[column_name] = header_value

    def set_align_cell(self, column_name, align_value):
        """set a align value for an existing displayed column."""
        self._align_cells[column_name] = align_value

    def add_custom_cell(self, builder):
        """Add specific cell class to format a column."""
        if not isinstance(builder, CellBuilder):
            msg = "1st argument (builder) must be an CellBuilder instance"
            raise ValueError(msg)
        self._custom_cells[builder.cell_name] = builder

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
        identifier = None
        for flag in self.cfg.keys():
            if getattr(args, flag, False):
                identifier = flag
                builder, clazz = self.cfg.get(flag).values()
                break
        if identifier is None:
            identifier = self.default_processor_identifier
            builder, clazz = self.cfg.get(identifier).values()
        if builder is None:
            builder = self.default_processor_builder_instance
        self.log.debug("builder: %s", builder)
        self.log.debug("clazz: %s", clazz)
        processor = builder(identifier, clazz)
        return processor

    def _load_custom_units(self, processor):
        for identifier, unit in self._units.items():
            if identifier in processor.units:
                processor.units[identifier] = unit

    def create(self, args=Namespace(), default_builder=None):
        """create a new processor and do the setup."""
        if default_builder:
            self.set_default_processor_builder(default_builder)
        self.log.debug("self.cfg: %s", self.cfg.keys())
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

        self._load_custom_units(processor)
        processor.setup(args)
        return processor
