#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests configuration and global fixtures."""


import sys
import logging
import pytest


@pytest.fixture(scope="session")
def logger():
    """Return global logger"""
    log = logging.getLogger("tests_vhatable")
    log.setLevel(logging.DEBUG)
    stdout = logging.StreamHandler(sys.stdout)
    log.addHandler(stdout)
    return log
