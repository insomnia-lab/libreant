'''
This module will connect to your elasticsearch instance.
An index will be reserved to the tests.
'''
from __future__ import print_function

from nose.tools import eq_, with_setup, ok_, raises

from . import db, cleanall


@with_setup(cleanall, cleanall)
def test_update_book_simple():
    '''Update a book, no merging'''
    id_ = db.add_book(doc_type='book',
                      body=dict(title='La fine', _language='it'))['_id']
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('fine')
    eq_(res['hits']['total'], 1)

    db.update_book(id_, doc_type='book',
                   body=dict(title='Ciao mondo', _language='it'))
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('fine')
    eq_(res['hits']['total'], 0)
    res = db.get_books_simplequery('mondo')
    eq_(res['hits']['total'], 1)


@with_setup(cleanall, cleanall)
def test_update_book_merge():
    '''Update a book, merging'''
    id_ = db.add_book(doc_type='book',
                      body=dict(title='La fine', _language='it'))['_id']
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('fine')
    eq_(res['hits']['total'], 1)

    db.update_book(id_, doc_type='book',
                   body=dict(foo='Ciao mondo', _language='it'))
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('fine')
    eq_(res['hits']['total'], 1)
    res = db.get_books_simplequery('mondo')
    eq_(res['hits']['total'], 1)


@with_setup(cleanall, cleanall)
def test_update_book_merge_fts_correct():
    '''Update a book, merging. FTS fields should still be correct'''
    id_ = db.add_book(doc_type='book',
                      body=dict(title='La fine', _language='it'))['_id']
    db.es.indices.refresh(index=db.index_name)
    db.update_book(id_, doc_type='book',
                   body=dict(foo='Ciao mondo', _language='it'))
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('mondo')
    src = res['hits']['hits'][0]['_source']
    ok_('mondo' in src['_text_it'])
    ok_('fine' in src['_text_it'])


@raises(Exception)
@with_setup(cleanall, cleanall)
def test_update_nonexisting_download_count():
    id_ = db.add_book(doc_type='book',
                      body=dict(title='La fine', _language='it'))['_id']
    db.increment_download_count(id_, 0)


@raises(Exception)
@with_setup(cleanall, cleanall)
def test_download_count_mandatory():
    '''
    if you omit the field download_count, increment_download_count will fail
    '''
    id_ = db.add_book(doc_type='book',
                      body=dict(title='La fine', _language='it',
                                _files=[dict(
                                    name='foo'
                                )]))['_id']
    db.increment_download_count(id_, 0)


@with_setup(cleanall, cleanall)
def test_update_download_count():
    id_ = db.add_book(doc_type='book',
                      body=dict(title='La fine', _language='it',
                                _files=[dict(
                                    download_count=0,
                                    name='foo'
                                )]))['_id']
    for i in xrange(1, 5):
        db.increment_download_count(id_, 0)
        book = db.get_book_by_id(id_)
        eq_(book['_source']['_files'][0]['download_count'], i)


@with_setup(cleanall, cleanall)
def test_update_download_count():
    ''' download count shouldn't modify other fields '''
    id_ = db.add_book(doc_type='book',
                      body=dict(title='La fine', _language='it',
                                _files=[dict(
                                    download_count=4,
                                    name='foo'
                                )]))['_id']
    prev = db.get_book_by_id(id_)
    db.increment_download_count(id_, 0)
    after = db.get_book_by_id(id_)
    prev['_source']['_files'][0]['download_count'] += 1
    eq_(prev['_source'], after['_source'])
