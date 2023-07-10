#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


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
# Copyright 2021 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#


import os
import sys
import json
import inspect
import argparse
import logging
import requests

from vhatable.processors import ProcessorBuilder
from vhatable.processors import ProcessorFactory
from vhatable.cellv2 import DateCellBuilder
from vhatable.cellv2 import ComplexCellBuilder
from vhatable.filters import PartialOr


def helper_print_header(extra=None):
    """Just a tiny helper to display a header between each rendering."""
    print("")
    print("=========================================")
    if extra:
        print(extra)
    print("")


def get_default_args():
    """This method allows to return a object containing some properties or
    arguments that can be provided by command line argiments like argparse
    """
    args = argparse.Namespace()
    args.verbose = False
    args.extended = False
    args.vertical = False
    args.raw = False
    args.debug = 0
    return args


def sample1():
    """Just a sample"""
    args = get_default_args()
    factory = ProcessorFactory()
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    builder = DateCellBuilder("date", millisecond=True)
    factory.add_custom_cell(builder)

    args = argparse.Namespace(debug=2, reverse=True, sort_by="name")
    processor = factory.create(args)

    processor.column_names = ["name", "size", "date"]
    processor.post_init()

    rows = [
        {"name": "value1", "date": 1625647954855, "size": 80000000},
        {"name": "value2", "date": 1625647954861, "size": 110000},
        {"name": "value3", "date": 1625647954890, "size": 280000000000},
        {"name": "value4", "date": 1625647954905, "size": 21000000000000},
        {"name": "value5", "date": 1625647954962, "size": 2100000000000000},
    ]
    processor.load(rows)

    helper_print_header("    >>>> Default  <<<<")
    print(processor)
    processor.run()


class API:
    """TODO"""
    URL = "https://epguides.frecar.no/show/bigbangtheory/"
    cacheFileName = "/tmp/vhatable-cache-big-bang.json"

    def load_json(self):
        """TODO"""
        # pylint: disable=unspecified-encoding
        data = None
        if os.path.isfile(self.cacheFileName):
            with open(self.cacheFileName) as user_file:
                file_contents = user_file.read()
                data = json.loads(file_contents)
        else:
            data = requests.get(self.URL, timeout=1).json()
            with open(self.cacheFileName, 'w') as json_file:
                json.dump(data, json_file)
        return data

    def list(self):
        """TODO"""
        json_data = self.load_json()
        for season in json_data:
            for episode in json_data[season]:
                yield episode

    def column_names(self):
        """TODO"""
        return ["season", "number", "title", "release_date", "show"]


def sample2():
    """Just a sample"""

    args = argparse.Namespace(
            debug=2,
            sort_reverse=False,
            sort_sort_by="season",
            # slice_end=40,
            # slice_limit=20,
            release_dates=[],
            titles=[],
            vertical=False)
    args.titles = ["ation"]
    args.release_dates = ["2016"]
    # args.sort_sort_by = "release_date"

    factory = ProcessorFactory()
    factory.add_filters(PartialOr("title", args.titles, True))
    factory.add_filters(PartialOr("release_date", args.release_dates))
    factory.add_custom_cell(
        ComplexCellBuilder(
            "show",
            fmt='{title}\n{imdb_id} {epguide_name}',
            fmtv='{title} {imdb_id} {epguide_name}'
        )
    )
    api = API()
    factory.set_default_processor_builder(
        ProcessorBuilder(
            autoload=False,
            rows=api.list(),
            column_names=api.column_names()
        )
    )

    processor = factory.create(args)

    helper_print_header("    >>>> Default  <<<<")
    print(processor)
    processor.run()
    print()


def sample3():
    """Just a sample"""

    args = argparse.Namespace(
            debug=2,
            sort_reverse=False,
            sort_sort_by="season",
            release_dates=[],
            slice_end=40,
            slice_limit=20,
            titles=[],
            vertical=False)

    api = API()
    factory = ProcessorFactory()
    factory.add_filters(PartialOr("title", args.titles, True))
    factory.add_filters(PartialOr("release_date", args.release_dates))
    factory.add_custom_cell(
        ComplexCellBuilder(
            "show",
            fmt='{title}\n{imdb_id} {epguide_name}',
            fmtv='{title} {imdb_id} {epguide_name}'
        )
    )
    factory.set_align_cell("title", "l")
    factory.set_align_cell("show", "c")

    processor = factory.create(
            args,
            default_builder=ProcessorBuilder(api=api, autoload=True))

    helper_print_header("    >>>> Default  <<<<")
    print(processor)
    processor.run()
    print()


def main():
    """ Main entrypoint of this sample program."""
    logging.basicConfig(level=logging.INFO)
    map_sample = {}
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isfunction(obj) and name.startswith('sample'):
            map_sample[name] = obj

    parser = argparse.ArgumentParser(description='Display some samples')
    parser.add_argument(
        'sample', choices=map_sample.keys(),
        help='Choose the sample to display.')
    args = parser.parse_args()

    obj = map_sample[args.sample]
    print("Sample : ", args.sample, " :", obj.__doc__)
    obj()
