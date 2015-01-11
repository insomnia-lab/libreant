from __future__ import print_function

from nose.tools import eq_, raises

from .import api

validate_book = api.validate_book


@raises(ValueError)
def test_invalid_book():
    '''Book without language'''
    validate_book(dict(title='Un libro'))


def test_idempotent_simple():
    b = dict(title='Un libro', _language='it')
    b = validate_book(b)
    eq_(sorted(b.items()), sorted(validate_book(validate_book(b)).items()))
