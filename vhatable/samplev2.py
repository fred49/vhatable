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


import sys
import inspect
import argparse
import logging
import requests

from argparse import Namespace
from vhatable.factory import GenericBuilder
from vhatable.factory import TableFactory
from vhatable.cellv2 import DateCellBuilder
from vhatable.cellv2 import ComplexCellBuilder
from vhatable.filters import PartialOr

from .corev2 import HTableProcessor
from .corev2 import VTableProcessor
from .corev2 import CountProcessor
from .corev2 import JsonProcessor
from .corev2 import CsvProcessor


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
    factory = TableFactory()
    factory.add_filters(PartialOr("name", ["value2", "value3"], True))
    builder = DateCellBuilder("date", millisecond=True)
    factory.set_custom_cell("date", builder)

    args = Namespace(debug=2, reverse=True, sort_by="name")
    table = factory.build(args)

    table.column_names = ["name", "size", "date"]

    rows = [
        {"name": "value1", "date": 1625647954855, "size": 80000000},
        {"name": "value2", "date": 1625647954861, "size": 110000},
        {"name": "value3", "date": 1625647954890, "size": 280000000000},
        {"name": "value4", "date": 1625647954905, "size": 21000000000000},
        {"name": "value5", "date": 1625647954962, "size": 2100000000000000},
    ]
    table.load(rows)

    helper_print_header("    >>>> Default  <<<<")
    table.run()


def sample2():
    """Just a sample"""

    class API:

        URL = "https://epguides.frecar.no/show/bigbangtheory/"

        def list(self):
            r = requests.get(self.URL)
            json = r.json()
            for season in json:
                for episode in json[season]:
                    yield episode

    args = Namespace(
            debug=2,
            sort_reverse=False,
            sort_sort_by="season",
            # slice_end=40,
            # slice_limit=20,
            release_dates=[],
            titles=[],
            vertical=False)
    args.titles = ["ation"]
    args.release_dates = ["2016"],
    # args.sort_sort_by = "release_date"

    api = API()
    builder = GenericBuilder(rows=api.list())
    factory = TableFactory(builder=builder)
    factory.add_filters(PartialOr("title", args.titles, True))
    factory.add_filters(PartialOr("release_date", args.release_dates))
    factory.set_custom_cell(
            "show", ComplexCellBuilder(
                "show",
                fmt='{title}\n{imdb_id} {epguide_name}',
                fmtv='{title} {imdb_id} {epguide_name}'
            )
    )
    processor = factory.build(args)
    processor.column_names = ["season", "number", "title", "release_date",
                              "show"]

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
