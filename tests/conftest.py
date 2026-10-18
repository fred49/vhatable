#!/usr/bin/env python
"""Tests configuration and global fixtures."""


import logging

import pytest


@pytest.fixture(name="logger", scope="session")
def fixture_logger():
    """Return global logger"""
    log = logging.getLogger("tests_vhatable")
    return log


@pytest.fixture(name="print_and_count", scope="session")
def fixture_print_and_count(logger):
    """TODO"""
    def inner_print_res(rows):
        res = list(rows)
        logger.info("\nbegin print_and_count")
        cpt = 0
        for row in res:
            cpt += 1
            logger.info("row: %s", row)
        logger.info("end print_and_count")
        return cpt
    return inner_print_res
