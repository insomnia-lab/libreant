'''
This module will connect to your elasticsearch instance.
An index will be reserved to the tests.
'''

from nose.tools import eq_, with_setup, raises

from libreantdb import api
from . import db, cleanall


@with_setup(cleanall)
def test_start_hasindex():
    '''If the test is setup properly, we got our own index'''
    assert db.es.indices.exists(db.index_name)


@with_setup(cleanall)
def notest_start_empty():
    '''If the test is setup properly, it's all empty'''
    assert not db.get_all_books()['hits']['hits']


@with_setup(cleanall, cleanall)
def test_add():
    '''Add should not complain'''
    db.add_book(doc_type='book',
                body=dict(title='Un libro', _language='it'))


@with_setup(cleanall, cleanall)
def test_addget():
    '''Coherence (by title)'''
    db.es.indices.refresh(index=db.index_name)

    db.add_book(doc_type='book',
                body=dict(title='Un libro', _language='it'))
    db.es.indices.refresh(index=db.index_name)

    res = db.get_books_by_title('libro')
    eq_(res['hits']['total'], 1)


@with_setup(cleanall, cleanall)
def test_addget_simple():
    '''Coherence (simple)'''
    db.es.indices.refresh(index=db.index_name)

    db.add_book(doc_type='book',
                body=dict(title='Un libro', _language='it'))
    db.es.indices.refresh(index=db.index_name)

    res = db.get_books_simplequery('libro')
    eq_(res['hits']['total'], 1)


@with_setup(cleanall, cleanall)
@raises(ValueError)
def test_invalid_book():
    '''Book without language'''
    db.add_book(doc_type='book', body=dict(title='Un libro'))


def test_allfields():
    """
    when adding a book, a new field must be added with the purpose of fts
    """
    body = {'title': "Ok computer",
            'actors': ["mazinga", "batman"],
            '_language': 'it'
            }
    body = api.validate_book(body)
    assert '_text_it' in body
    words = ('Ok', 'computer', 'mazinga', 'batman')
    for word in words:
        assert word in body['_text_it'], body['_text_it']
