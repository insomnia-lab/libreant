'''
This module will connect to your elasticsearch instance.
An index will be reserved to the tests.
'''
from __future__ import print_function

from nose.tools import eq_, with_setup, ok_

from . import db, cleanall


@with_setup(cleanall, cleanall)
def test_update_book_simple():
    '''Update a book, no merging'''
    id_ = db.add_book(doc_type='book',
                      body=dict(title='La fine', language='it'))['_id']
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('fine')
    eq_(res['hits']['total'], 1)

    db.update_book(id_, doc_type='book',
                   body=dict(title='Ciao mondo', language='it'))
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('fine')
    eq_(res['hits']['total'], 0)
    res = db.get_books_simplequery('mondo')
    eq_(res['hits']['total'], 1)


@with_setup(cleanall, cleanall)
def test_update_book_merge():
    '''Update a book, merging'''
    id_ = db.add_book(doc_type='book',
                      body=dict(title='La fine', language='it'))['_id']
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('fine')
    eq_(res['hits']['total'], 1)

    db.update_book(id_, doc_type='book',
                   body=dict(foo='Ciao mondo', language='it'))
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('fine')
    eq_(res['hits']['total'], 1)
    res = db.get_books_simplequery('mondo')
    eq_(res['hits']['total'], 1)


@with_setup(cleanall, cleanall)
def test_update_book_merge_fts_correct():
    '''Update a book, merging. FTS fields should still be correct'''
    id_ = db.add_book(doc_type='book',
                      body=dict(title='La fine', language='it'))['_id']
    db.es.indices.refresh(index=db.index_name)
    db.update_book(id_, doc_type='book',
                   body=dict(foo='Ciao mondo', language='it'))
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('mondo')
    src = res['hits']['hits'][0]['_source']
    ok_('mondo' in src['text_it'])
    ok_('fine' in src['text_it'])
