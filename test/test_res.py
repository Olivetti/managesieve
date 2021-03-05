#!/usr/bin/env python
"""
Unit test patterns in for managesieve.py
"""

__author__ = "Hartmut Goebel <h.goebel@crazy-compilers.com>"
__copyright__ = "(c) Copyright 2003-2021 by Hartmut Goebel"
__license__ = "GNU General Public License, version 3"

import pytest

from managesieve import Oknobye

parameters = [
    ('OK',                         ('OK', None, None)),
    ('OK (OKAY/ALL)',              ('OK', 'OKAY/ALL', None)),
    ('OK "Hi di How!"',            ('OK', None, '"Hi di How!"')),
    ('OK (OKAY/ALL) "Hi di How!"', ('OK', 'OKAY/ALL', '"Hi di How!"')),
    ]
ids = [p[0] for p in parameters]


@pytest.mark.parametrize("string, expected", parameters, ids=ids)
def test_Oknobye_pattern(string, expected):
    mo = Oknobye.match(string)
    assert mo.group('type', 'code', 'data') == expected
    expected = dict(zip(('type', 'code','data'), expected))
    assert mo.groupdict() == expected
