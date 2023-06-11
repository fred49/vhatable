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


# pylint: skip-file
# flake8: noqa
# Deprecated module

import sys
import time
import inspect
import argparse
import logging

from linshareapi.core import ResourceBuilder
from vhatable.core import Action
from vhatable.core import TableFactory
from vhatable.core import SampleAction
from vhatable.cell import CellBuilder
from vhatable.cell import ComplexCellBuilder
from vhatable.filters import PartialOr
from vhatable.filters import PartialDate


class AbstractEndpoint:
    """Abstract class for all endpoint classes"""

    last_id = 0
    my_list = []

    def _get_next_id(self):
        self.last_id += 1
        return self.last_id

    def list(self):
        """Return all elements from the list"""
        return self.my_list

    def get(self, elt_id):
        """Get a element from the list"""
        for elt in self.my_list:
            if elt["id"] == elt_id:
                return elt
        return None

    def delete(self, elt_id):
        """Delete an element from the list"""
        found = False
        for elt in self.my_list:
            if elt["id"] == elt_id:
                self.my_list.remove(elt)
                found = True
        return found

    def update(self, obj):
        """Update an element from the list, only name is supported."""
        found = False
        for elt in self.my_list:
            if elt["id"] == obj["id"]:
                elt["name"] = obj["name"]
                elt["modificationDate"] = time.time()
                found = True
        return found


class Endpoint1(AbstractEndpoint):
    """Sample of an Endpoint1"""

    def __init__(self):
        self.my_list = [
            {
                "creationDate": 1625647954855,
                "modificationDate": 1625647954855,
                "name": "My first element",
                "id": 1
            },
            {
                "creationDate": 1630922388966,
                "modificationDate": 1630922389147,
                "name": "My second element",
                "id": 2
            },
            {
                "creationDate": 1631023612633,
                "modificationDate": 1631023612862,
                "name": "My third element",
                "id": 3
            },
            {
                "creationDate": 1631105647241,
                "modificationDate": 1631105647309,
                "name": "My forth element",
                "id": 4
            },
            {
                "creationDate": 1631194331337,
                "modificationDate": 1631194331444,
                "name": "My fifth element",
                "id": 5
            }
        ]
        self.last_id = 5

    def create(self, obj):
        """Create an element and add it to the list"""
        elt = {}
        elt["id"] = self._get_next_id()
        elt["name"] = obj["name"]
        elt["creationDate"] = time.time()
        elt["modificationDate"] = time.time()
        self.my_list.append(elt)
        return elt

    def get_rbu(self):
        """FIXME"""
        # pylint: disable=no-self-use
        rbu = ResourceBuilder("element")
        rbu.add_field('id')
        rbu.add_field('name', required=True)
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate', extended=True)
        return rbu


class Endpoint2(AbstractEndpoint):
    """Sample of an Endpoint2"""

    def __init__(self):
        self.my_list = [
            {
                "creationDate": 1625647954855,
                "modificationDate": 1625647954855,
                "name": "My first element",
                "foo": 0.51,
                "id": 1
            },
            {
                "creationDate": 1630922388966,
                "modificationDate": 1630922389147,
                "name": "My second element",
                "foo": 0.07,
                "id": 2
            },
            {
                "creationDate": 1631023612633,
                "modificationDate": 1631023612862,
                "name": "My third element",
                "foo": 0.3,
                "id": 3
            },
            {
                "creationDate": 1631105647241,
                "modificationDate": 1631105647309,
                "name": "My forth element",
                "foo": 0.2,
                "id": 4
            },
            {
                "creationDate": 1631194331337,
                "modificationDate": 1631194331444,
                "name": "My fifth element",
                "foo": 0.43,
                "id": 5
            }
        ]
        self.last_id = 5

    def create(self, obj):
        """Create an element and add it to the list"""
        elt = {}
        elt["id"] = self._get_next_id()
        elt["name"] = obj["name"]
        elt["creationDate"] = time.time()
        elt["modificationDate"] = time.time()
        elt["foo"] = 0.02
        self.my_list.append(elt)
        return elt

    def get_rbu(self):
        """FIXME"""
        # pylint: disable=no-self-use
        rbu = ResourceBuilder("element")
        rbu.add_field('id')
        rbu.add_field('name', required=True)
        rbu.add_field('foo')
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate', extended=True)
        return rbu


class Endpoint3(AbstractEndpoint):
    """Sample of an Endpoint2"""

    def __init__(self):
        self.my_list = [
            {
                "creationDate": 1625647954855,
                "modificationDate": 1625647954855,
                "name": "My first element",
                "foo": 0.01,
                "foo_complex": {
                    "name": "nested object",
                    "uuid": "f05e7292-e00e-4bd8-94e2-3f9c3316071f"
                },
                "id": 1
            },
            {
                "creationDate": 1630922388966,
                "modificationDate": 1630922389147,
                "name": "My second element",
                "foo": 0.07,
                "foo_complex": {
                    "name": "nested object",
                    "uuid": "f06e7292-e00e-4bd8-94e2-3f9c3316071f"
                },
                "id": 2
            },
            {
                "creationDate": 1631023612633,
                "modificationDate": 1631023612862,
                "name": "My third element",
                "foo": 0.1,
                "foo_complex": {
                    "name": "nested object",
                    "uuid": "f07e7292-e00e-4bd8-94e2-3f9c3316071f"
                },
                "id": 3
            },
            {
                "creationDate": 1631105647241,
                "modificationDate": 1631105647309,
                "name": "My forth element",
                "foo": 0.2,
                "foo_complex": {
                    "name": "nested object",
                    "uuid": "f08e7292-e00e-4bd8-94e2-3f9c3316071f"
                },
                "id": 4
            },
            {
                "creationDate": 1631194331337,
                "modificationDate": 1631194331444,
                "name": "My fifth element",
                "foo": 0.43,
                "foo_complex": {
                    "name": "nested object",
                    "uuid": "f09e7292-e00e-4bd8-94e2-3f9c3316071f"
                },
                "id": 5
            }
        ]
        self.last_id = 5

    def create(self, obj):
        """Create an element and add it to the list"""
        elt = {}
        elt["id"] = self._get_next_id()
        elt["name"] = obj["name"]
        elt["creationDate"] = time.time()
        elt["modificationDate"] = time.time()
        elt["foo"] = 0.02
        self.my_list.append(elt)
        return elt

    def get_rbu(self):
        """FIXME"""
        # pylint: disable=no-self-use
        rbu = ResourceBuilder("element")
        rbu.add_field('id')
        rbu.add_field('name', required=True)
        rbu.add_field('foo')
        rbu.add_field('foo_complex')
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate', extended=True)
        return rbu


class API:
    """ An sample api that may contain multiple endpoints, one by resource."""
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.endpoint1 = Endpoint1()
        self.endpoint2 = Endpoint2()
        self.endpoint3 = Endpoint3()


class SomeTitle(Action):
    """TODO"""

    display = True

    def init(self, args, cli, endpoint):
        super(SomeTitle, self).init(args, cli, endpoint)
        self.display = not getattr(args, 'no_title', False)

    def __call__(self, args, cli, endpoint, data):
        self.init(args, cli, endpoint)
        if self.display:
            print()
            print("###> Some Title")
            print()


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
    """First sample: Just some row data and tests."""
    api = API()
    for elt in api.endpoint1.list():
        print(elt)
    api.endpoint1.delete(3)
    print("--------")
    for elt in api.endpoint1.list():
        print(elt)
    print("--------")
    obj = {"name": "helloooooo"}
    obj = api.endpoint1.create(obj)
    for elt in api.endpoint1.list():
        print(elt)
    print("--------")
    obj["name"] = " Hello Foo"
    api.endpoint1.update(obj)
    for elt in api.endpoint1.list():
        print(elt)
    print("--------")

def sample2():
    """Three rendering: simple, with verbose and with extended flag on."""
    args = get_default_args()

    api = API()
    tbu = TableFactory(api, api.endpoint1, "creationDate")

    print("")
    print("=========================================")
    print("")
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

    args.verbose = True
    print("")
    print("=========================================")
    print("")
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

    args.extended = True
    print("")
    print("=========================================")
    print("")
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

def sample3():
    """Filtering displayed data by name """
    args = get_default_args()
    args.names = ["fi"]

    api = API()
    tbu = TableFactory(api, api.endpoint1, "creationDate")
    tbu.add_filters(
        PartialOr("name", args.names, True)
    )

    helper_print_header()
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

def sample4():
    """Filtering displayed data with raw dates"""
    args = get_default_args()
    args.raw = True
    args.extended = True
    api = API()
    tbu = TableFactory(api, api.endpoint1, "creationDate")
    helper_print_header()
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

def sample5():
    """Filtering displayed data by creationDate"""
    args = get_default_args()
    args.cdate = "2021-07-07"
    args.raw = True
    api = API()
    tbu = TableFactory(api, api.endpoint1, "creationDate")
    tbu.add_filters(
        PartialDate("creationDate", args.cdate)
    )
    helper_print_header()
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

def sample6():
    """Using some title/header to the list."""
    args = get_default_args()
    api = API()
    tbu = TableFactory(api, api.endpoint1, "creationDate")

    helper_print_header("    >>>> Without a title <<<<")
    args.no_title=True
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

    helper_print_header("    >>>> With a title <<<<")
    args.no_title=False
    tbu.add_pre_render_class(SomeTitle())
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

def sample7():
    """Using CellBuilder to format the content of a colum."""
    args = get_default_args()
    # args.debug = 3
    api = API()
    tbu = TableFactory(api, api.endpoint2, "creationDate")
    # https://docs.python.org/3/library/string.html#format-specification-mini-language
    tbu.add_custom_cell("foo", CellBuilder('{value:.2%}', '{value:.8%}'))

    helper_print_header("    >>>> Raw data <<<<")
    args.raw = True
    tbu.load_args(args).build().load_v2(api.endpoint2.list()).render()

    helper_print_header("    >>>> Formated data <<<<")
    args.raw = False
    tbu.load_args(args).build().load_v2(api.endpoint2.list()).render()

def sample8():
    """Using CellBuilder and vertical mode """
    args = get_default_args()
    api = API()
    tbu = TableFactory(api, api.endpoint2, "creationDate")
    # https://docs.python.org/3/library/string.html#format-specification-mini-language
    tbu.add_custom_cell("foo", CellBuilder('{value:.2%}', '{value:.8%}'))
    # CellBuilder('horizontal format', 'vertical format', 'filter format'))
    # When you will try to use a Equal filter for example, 'filter format' will
    # be used to format the content of the cell before testing the equality.

    helper_print_header("    >>>> Horizontal mode <<<<")
    tbu.load_args(args).build().load_v2(api.endpoint2.list()).render()

    helper_print_header("    >>>> Vertical mode <<<<")
    args.vertical = True
    tbu.load_args(args).build().load_v2(api.endpoint2.list()).render()

def sample9():
    """Using ComplexCellBuilder and vertical mode """
    args = get_default_args()
    api = API()
    tbu = TableFactory(api, api.endpoint3, "creationDate")
    # https://docs.python.org/3/library/string.html#format-specification-mini-language
    tbu.add_custom_cell("foo", CellBuilder('{value:.2%}', '{value:.8%}'))
    # CellBuilder('horizontal format', 'vertical format', 'filter format'))
    # When you will try to use a Equal filter for example, 'filter format' will
    # be used to format the content of the cell before testing the equality.
    tbu.add_custom_cell("foo_complex", ComplexCellBuilder(
        '{name} ({uuid:.8})',
        '{name} ({uuid})'
    ))

    helper_print_header("    >>>> Horizontal mode <<<<")
    tbu.load_args(args).build().load_v2(api.endpoint3.list()).render()

    helper_print_header("    >>>> Vertical mode <<<<")
    args.vertical = True
    tbu.load_args(args).build().load_v2(api.endpoint3.list()).render()

def sample10():
    """Using count_only flag to disable rendering and displayed only the count
    of elements. Using cli_mode to displayed only essential data.
    """
    args = get_default_args()
    api = API()
    tbu = TableFactory(api, api.endpoint1, "creationDate",
                       cli_mode_identifier="id")
    # tbu.add_action
    helper_print_header("    >>>> count mode <<<<")
    args.count_only=True
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

    helper_print_header("    >>>> cli mode: only id column is displayed <<<<")
    args.cli_mode=True
    args.count_only=False
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

    helper_print_header("    >>>> cli mode: only count result is displayed <<<<")
    args.cli_mode=True
    args.count_only=True
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

def sample11():
    """Using SampleAction to illustrate custom behaviour that can be triggered by a simple flag.
    This SampleAction does not nothing except displaying data passed to this action.
    For example, you can use an action to delete some row.
    """
    args = get_default_args()
    args.names = ["My fi"]
    api = API()
    tbu = TableFactory(api, api.endpoint1, "creationDate")
    tbu.add_filters(
        PartialOr("name", args.names, True)
    )
    tbu.add_action('display_sample', SampleAction("Just a sample action"))

    helper_print_header("    >>>> Normal mode <<<<")
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

    helper_print_header("    >>>> Action mode <<<<")
    args.display_sample=True
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

def sample12():
    """Sample using limit, end and start keywords"""
    args = get_default_args()
    args.limit = 0
    args.start = 0
    args.end = 0

    api = API()
    tbu = TableFactory(api, api.endpoint1, "creationDate")

    helper_print_header("    >>>> limit to last 2 elements <<<<")
    args.end = 2
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

    helper_print_header("    >>>> limit to first 2 elements <<<<")
    args.end = 0
    args.limit = 2
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

    helper_print_header("    >>>> skip the first 2 rows and then limit to first 2 elements <<<<")
    args.end = 0
    args.limit = 2
    args.start = 2
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

def sample13():
    """Sample using reverse or sort_by keywords"""
    args = get_default_args()
    args.extended = True

    api = API()
    tbu = TableFactory(api, api.endpoint2, "creationDate")

    helper_print_header("    >>>> Default  <<<<")
    tbu.load_args(args).build().load_v2(api.endpoint2.list()).render()

    helper_print_header("    >>>> Sort by foo  <<<<")
    args.sort_by = "foo"
    tbu.load_args(args).build().load_v2(api.endpoint2.list()).render()

    helper_print_header("    >>>> Sort by foo reverse <<<<")
    args.sort_by = "foo"
    args.reverse = True
    tbu.load_args(args).build().load_v2(api.endpoint2.list()).render()

def sample14():
    """Sample csv mode"""
    args = get_default_args()

    api = API()
    tbu = TableFactory(api, api.endpoint2, "creationDate")

    helper_print_header("    >>>> CSV  <<<<")
    args.csv = True
    tbu.load_args(args).build().load_v2(api.endpoint2.list()).render()

    helper_print_header("    >>>> CSV without header  <<<<")
    args.no_headers = True
    tbu.load_args(args).build().load_v2(api.endpoint2.list()).render()

def sample15():
    """Sample json mode"""
    args = get_default_args()

    api = API()
    tbu = TableFactory(api, api.endpoint2, "creationDate")
    # we override the list of the fields we want to display
    tbu.fields = ["id", "name"]

    helper_print_header("    >>>> Default  <<<<")
    args.end = 2
    tbu.load_args(args).build().load_v2(api.endpoint2.list()).render()

    helper_print_header("    >>>> Json  <<<<")
    args.json = True
    tbu.load_args(args).build().load_v2(api.endpoint2.list()).render()

    helper_print_header("    >>>> raw json <<<<")
    args.raw_json = True
    tbu.load_args(args).build().load_v2(api.endpoint2.list()).render()

def sample16():
    """Sample csv mode"""
    args = get_default_args()
    args.csv = True

    api = API()
    tbu = TableFactory(api, api.endpoint2, "creationDate")

    helper_print_header("    >>>> Default  <<<<")
    tbu.load_args(args).build().load_v2(api.endpoint2.list()).render()


def main():
    """ Main entrypoint of this sample program."""
    logging.basicConfig(level=logging.INFO)
    map_sample = {}
    for name,obj in inspect.getmembers(sys.modules[__name__]):
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
