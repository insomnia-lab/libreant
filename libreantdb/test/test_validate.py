from nose.tools import eq_, raises, assert_raises

from libreantdb import api

validate_book = api.validate_book
collectStrings = api.collectStrings


@raises(ValueError)
def test_invalid_book():
    '''Book without language'''
    validate_book(dict(title='Un libro'))


def test_long_language():
    '''Book with language longer than two chars'''
    with assert_raises(ValueError) as cm:
        validate_book(dict(_language='long', title='Un libro'))
    exc = cm.exception
    eq_(exc.message, 'invalid language: long')


def test_idempotent_simple():
    b = dict(title='Un libro', _language='it')
    b = validate_book(b)
    eq_(sorted(b.items()), sorted(validate_book(validate_book(b)).items()))


def test_collect_empty():
    for empty in ([], '', {}):
        eq_(collectStrings(empty), [])
    eq_(collectStrings({'asd': [], 'foo': '', 'other': {}}), [])


def test_collect_ignore_underscore():
    eq_(collectStrings({'foo': 'ciao', '_other': 'foo'}), ['ciao'])
    eq_(sorted(collectStrings({'foo': 'ciao', 'other': 'foo'})),
        ['ciao', 'foo'])


def test_collect_other_types():
    for obj in 3, 2.7, set():
        eq_(collectStrings(obj), [])
