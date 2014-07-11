'''
This module will connect to your elasticsearch instance.
An index will be reserved to the tests.
'''
from __future__ import print_function
# from pprint import pprint

from nose.tools import eq_, with_setup, raises

from . import db, api


def setup_func():
    db.es.delete_by_query(index=db.index_name,
                          body={'query': {'match_all': {}}})
    db.es.indices.refresh(index=db.index_name)


def teardown_func():
    db.es.delete_by_query(index=db.index_name,
                          body={'query': {'match_all': {}}})


@with_setup(setup_func, teardown_func)
def test_start_hasindex():
    '''If the test is setup properly, we got our own index'''
    assert 'test-book' in db.es.indices.status()['indices']


@with_setup(setup_func, teardown_func)
def notest_start_empty():
    '''If the test is setup properly, it's all empty'''
    assert not db.get_all_books()['hits']['hits']


@with_setup(setup_func, teardown_func)
def test_add():
    '''Add should not complain'''
    db.add_book(doc_type='book',
                body=dict(title='Un libro', language='it'))


@with_setup(setup_func, teardown_func)
def test_addget():
    '''Coherence'''
    db.es.indices.refresh(index=db.index_name)

    eq_(db.get_books_by_title('libro')['hits']['total'], 0)
    db.add_book(doc_type='book',
                body=dict(title='Un libro', language='it'))
    db.es.indices.refresh(index=db.index_name)

    res = db.get_books_by_title('libro')
    eq_(res['hits']['total'], 1)


@with_setup(setup_func, teardown_func)
@raises(ValueError)
def test_invalid_book():
    db.add_book(doc_type='book', body=dict(title='Un libro'))


@with_setup(setup_func, teardown_func)
def test_allfields():
    """
    when adding a book, a new field must be added with the purpose of fts
    """
    body = {'title': "Ok computer",
            'actors': ["mazinga", "batman"],
            'language': 'it'
            }
    body = api.validate_book(body)
    assert 'text_it' in body
    words = ('Ok', 'computer', 'mazinga', 'batman')
    for word in words:
        assert word in body['text_it'], body['text_it']


@with_setup(setup_func, teardown_func)
def test_fts_basic():
    '''Simple fts, without stemming or anything fancy'''
    db.add_book(doc_type='book',
                body=dict(title='La fine', language='it'))
    db.add_book(doc_type='book',
                body=dict(title="It's fine", language='en'))
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('fine')
    eq_(res['hits']['total'], 2)
