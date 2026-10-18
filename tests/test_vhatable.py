#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Testing actions like rsync, hard links, ..."""


import logging
import time
import sys
import pytest

from linshareapi.core import ResourceBuilder
from vhatable.core import TableFactory


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
        found = None
        for elt in self.my_list:
            if elt["id"] == obj["id"]:
                elt["name"] = obj["name"]
                elt["modificationDate"] = time.time()
                found = elt
        return found


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


@pytest.fixture()
def api_1():
    """Create an new API object with one endoint"""

    class Endpoint(AbstractEndpoint):
        """Sample of an Endpoint"""

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


    class API:
        """ An sample api that may contain multiple endpoints, one by resource."""
        # pylint: disable=too-few-public-methods

        def __init__(self):
            # you may have a lot of endoint, one per handled resource
            self.endpoint = Endpoint()


    return API()


@pytest.fixture()
def api_2():
    """Create an new API object with one endoint"""

    class Endpoint(AbstractEndpoint):
        """Sample of an Endpoint"""

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
            return rbu


    class API:
        """ An sample api that may contain multiple endpoints, one by resource."""
        # pylint: disable=too-few-public-methods

        def __init__(self):
            # you may have a lot of endoint, one per handled resource
            self.endpoint = Endpoint()


    return API()


@pytest.fixture()
def logger():
    """Return global logger"""
    log = logging.getLogger("tests_vhatable")
    log.setLevel(logging.DEBUG)
    stdout = logging.StreamHandler(sys.stdout)
    log.addHandler(stdout)
    return log


@pytest.fixture()
def provide_default_args():
    """This method allows to return a object containing some properties or
    arguments that can be provided by command line argiments like argparse
    """

    # we could have used argparse.Namespace
    class Namespace:
        """Class to simulate argparse.Namespace, it is just a class that we
        contain some user inputs (cli, Configuration file, environment variable)
        """
        # pylint: disable=too-few-public-methods
        verbose = False
        extended = False
        vertical = False
        raw = False
        debug = 0
    return Namespace


def test_api_1(api_1, logger):
    """Testing api_1 fixture"""
    # pylint: disable=redefined-outer-name
    assert len(api_1.endpoint.list()) == 5
    assert api_1.endpoint.delete(3)
    assert len(api_1.endpoint.list()) == 4
    obj = {"name": "helloooooo"}
    obj = api_1.endpoint.create(obj)
    assert obj["name"] == "helloooooo"
    assert obj["id"] == 6
    assert len(api_1.endpoint.list()) == 5
    obj["name"] = " Hello Foo"
    obj2 = api_1.endpoint.update(obj)
    assert obj2
    assert obj["name"] == " Hello Foo"
    logger.debug("\nobj: %s", obj)
    logger.debug("obj2: %s", obj2)
    assert obj["creationDate"] == obj2["creationDate"]

def test_table_factory_verbose(api_1, provide_default_args, capsys, pytestconfig):
    """Testing verbose mode"""
    # pylint: disable=redefined-outer-name
    args = provide_default_args()

    tbu = TableFactory(api_1, api_1.endpoint, "creationDate")
    table = tbu.load_args(args).build().load_v2(api_1.endpoint.list())
    assert table.render()
    captured = capsys.readouterr()
    data = captured.out
    assert len(data) == 441
    rows = data.split('\n')
    assert len(rows) == 10
    assert len(rows[0]) == 48

    args.verbose = True
    table = tbu.load_args(args).build().load_v2(api_1.endpoint.list())
    assert table.render()
    captured = capsys.readouterr()
    data = captured.out
    if pytestconfig.getoption("verbose") > 2:
        with capsys.disabled():
            print(data)
    assert len(data) == 495
    rows = data.split('\n')
    assert len(rows) == 13
    assert len(rows[0]) == 48

    args.extended = True
    table = tbu.load_args(args).build().load_v2(api_1.endpoint.list())
    assert table.render()
    captured = capsys.readouterr()
    data = captured.out
    if pytestconfig.getoption("verbose") > 2:
        with capsys.disabled():
            print(data)
    assert len(data) == 693
    rows = data.split('\n')
    assert len(rows) == 13
    assert len(rows[0]) == 70


def test_table_factory_row_1(api_2, provide_default_args, logger):
    """Testing verbose mode"""
    # pylint: disable=redefined-outer-name
    args = provide_default_args()

    tbu = TableFactory(api_2, api_2.endpoint, "creationDate")
    table = tbu.load_args(args).build().load_v2(api_2.endpoint.list())
    assert table.render()
    data = table.get_raw()
    print(str(data))
    assert len(data) == 5
    assert len(data[0]) == 2
    assert data[0]["id"] == 1

def est_table_factory_verbose(api_1, provide_default_args, capsys, logger):
    """Testing verbose mode"""
    # pylint: disable=redefined-outer-name
    args = provide_default_args()

    tbu = TableFactory(api_1, api_1.endpoint, "creationDate")
    table = tbu.load_args(args).build().load_v2(api_1.endpoint.list())
    assert table.render()
    data = table.get_json()
    with capsys.disabled():
        print(str(data))
    captured = capsys.readouterr()
    with capsys.disabled():
        print(captured.out)
    assert len(captured.out) == 442
    args.verbose = True
    #assert tbu.load_args(args).build().load_v2(api_1.endpoint.list()).render()

def est_sample2(api_1, provide_default_args):
    """Testing verbose mode"""
    # pylint: disable=redefined-outer-name
    args = provide_default_args()

    tbu = TableFactory(api_1, api_1.endpoint, "creationDate")

    print("")
    print("=========================================")
    print("")
    assert tbu.load_args(args).build().load_v2(api_1.endpoint.list()).render()

    args.verbose = True
    print("")
    print("=========================================")
    print("")
    assert tbu.load_args(args).build().load_v2(api_1.endpoint.list()).render()

    args.extended = True
    print("")
    print("=========================================")
    print("")
    assert tbu.load_args(args).build().load_v2(api_1.endpoint.list()).render()
