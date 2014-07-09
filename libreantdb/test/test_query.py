'''
This module will connect to your elasticsearch instance.
An index will be reserved to the tests.
'''
from pprint import pprint

from nose.tools import eq_

from . import db


def test_start_hasindex():
    '''If the test is setup properly, we got our own index'''
    assert 'test-book' in db.es.indices.status()['indices']


def notest_start_empty():
    '''If the test is setup properly, it's all empty'''
    assert not db.get_all_books()['hits']['hits']


def test_addget():
    '''Coherence'''
    db.es.indices.refresh(index=db.index_name)

    eq_(db.get_books_by_title('libro')['hits']['total'], 0)
    db.add_book(doc_type='book', body=dict(title='Un libro'))
    db.es.indices.refresh()

    res = db.get_books_by_title('libro')
    eq_(res['hits']['total'], 1)
