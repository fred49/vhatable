#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


# This file is part of Linshare cli.
#
# LinShare cli is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LinShare cli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LinShare cli.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2021 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#


import sys
import time
import inspect
import argparse
import logging

from linshareapi.core import ResourceBuilder
from vhatable.core import TableFactory
from vhatable.filters import PartialOr
from vhatable.filters import PartialDate



class Endpoint1:
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

    def create(self, obj):
        """Create an element and add it to the list"""
        elt = {}
        elt["id"] = self._get_next_id()
        elt["name"] = obj["name"]
        elt["creationDate"] = time.time()
        elt["modificationDate"] = time.time()
        self.my_list.append(elt)
        return elt

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

    def get_rbu(self):
        """FIXME"""
        rbu = ResourceBuilder("element")
        rbu.add_field('id')
        rbu.add_field('name', required=True)
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate', extended=True)
        return rbu


class API:
    """ An sample api that may contain multiple endpoints, one by resource."""
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.endpoint1 = Endpoint1()



def helper_print_header():
    print("")
    print("=========================================")
    print("")

def get_default_args():
    """This method allows to return a object containing some properties or
    arguments that can be provided by command line argiments like argparse
    """
    args = argparse.Namespace()
    args.verbose = False
    args.extended = False
    # args.debug = False
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
    """TODO"""
    args = get_default_args()
    api = API()
    tbu = TableFactory(api, api.endpoint1, "creationDate")
    # tbu.add_action
    # tbu.add_custom_cell
    # tbu.add_pre_render_class
    # tbu.add_filter_cond
    helper_print_header()
    tbu.load_args(args).build().load_v2(api.endpoint1.list()).render()

def main():
    """ Main entrypoint of this sample program."""
    logging.basicConfig(level=logging.DEBUG)
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
