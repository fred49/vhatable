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
from .corev2 import VTableProcessor
from .corev2 import CountProcessor
from .corev2 import JsonProcessor
from .corev2 import CsvProcessor


class GenericBuilder:
    """This builder is design to be used by the factory to create a processor.
    It will create the processor and passing some default arguments to the
    constructor. It could be extended to provide some extra parameters to a
    specific processor.
    """

    def __init__(self, debug=0, rows=None, column_names=None,
                 autokeys=True):
        self.debug = debug
        self.rows = rows
        self.autokeys = autokeys
        self.column_names = column_names

    def __call__(self, clazz):
        processor = clazz(
                debug=self.debug,
                autokeys=self.autokeys,
                column_names=self.column_names,
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


class ProcessorFactory:
    """class in charge of creating to proper processor according input args.
    This class is also in charge of proviging all processor's config.
    """

    def _create_cfg(self, builder, clazz):
        return {
            "builder": builder,
            "clazz": clazz
        }

    def __init__(self, builder=GenericBuilder()):
        """TODO"""
        classname = self.__class__.__name__
        self.log = logging.getLogger('vhatable.' + classname)

        self.cfg = OrderedDict()
        self.cfg['count'] = self._create_cfg(builder, CountProcessor)
        self.cfg['cli_mode'] = self._create_cfg(builder, CountProcessor)
        self.cfg['vertical'] = self._create_cfg(builder, VTableProcessor)
        self.cfg['csv'] = self._create_cfg(builder, CsvProcessor)
        self.cfg['json'] = self._create_cfg(builder, JsonProcessor)
        self.default = self._create_cfg(builder, HTableProcessor)

        self._custom_cells = {}
        self._header_cells = {}
        self._align_cells = {}
        self._filters = []
        self._pre_render_classes = []

    def set_header_cell(self, column_name, header_value):
        """set a header value for an existing displayed column."""
        self._header_cells[column_name] = header_value

    def set_align_cell(self, column_name, align_value):
        """set a align value for an existing displayed column."""
        self._align_cells[column_name] = align_value

    def set_custom_cell(self, column, builder):
        """Add specific cell class to format a column."""
        self._custom_cells[column] = builder

    def set_action(self, flag, builder, processor_clazz):
        """Add some custom action class trigger by a flag."""
        if not isinstance(builder, GenericBuilder):
            msg = "2th argument (builder) must be an GenericBuilder instance"
            raise ValueError(msg)
        self.cfg[flag] = self._create_cfg(builder, processor_clazz)

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
            builder, clazz = self.default.values()
        self.log.debug("builder: %s", builder)
        self.log.debug("clazz: %s", clazz)
        processor = builder(clazz)
        self.log.debug("processor: %s", processor)
        return processor

    def build(self, args=Namespace()):
        """build the processor and do the setup."""
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
