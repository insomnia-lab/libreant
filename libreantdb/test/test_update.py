'''
This module will connect to your elasticsearch instance.
An index will be reserved to the tests.
'''

from nose.tools import eq_, with_setup, ok_, raises

from elasticsearch import ConflictError
from . import db, cleanall


@with_setup(cleanall, cleanall)
def test_update_book_simple():
    '''Update a book, no merging'''
    id_ = db.add_book(body=dict(title='La fine', _language='it'))['_id']
    db.es.indices.refresh(index=db.index_name)
    db.update_book(id_, dict(title='Ciao mondo'))
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('fine')
    eq_(res['hits']['total'], 0)
    res = db.get_books_simplequery('mondo')
    eq_(res['hits']['total'], 1)

@with_setup(cleanall, cleanall)
def test_update_book_merge():
    '''Update a book, merging'''
    id_ = db.add_book(body=dict(title='La fine', _language='it'))['_id']
    db.es.indices.refresh(index=db.index_name)
    db.update_book(id_, dict(foo='Ciao mondo'))
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('fine')
    eq_(res['hits']['total'], 1)
    res = db.get_books_simplequery('mondo')
    eq_(res['hits']['total'], 1)

@with_setup(cleanall, cleanall)
def test_update_book_language():
    '''Update book language'''
    id_ = db.add_book(body=dict(title='La fine', _language='it'))['_id']
    db.es.indices.refresh(index=db.index_name)
    db.update_book(id_, dict(title='Ciao mondo', _language='en'))
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('fine')
    eq_(res['hits']['total'], 0)
    res = db.get_books_simplequery('mondo')
    eq_(res['hits']['total'], 1)

@with_setup(cleanall, cleanall)
def test_update_book_merge_fts_correct():
    '''Update a book, merging. FTS fields should still be correct'''
    id_ = db.add_book(body=dict(title='La fine', _language='it'))['_id']
    db.es.indices.refresh(index=db.index_name)
    db.update_book(id_, dict(foo='Ciao mondo'))
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('mondo')
    src = res['hits']['hits'][0]['_source']
    ok_('mondo' in src['_text_it'])
    ok_('fine' in src['_text_it'])

@with_setup(cleanall, cleanall)
def test_modify_book():
    id = db.add_book(body=dict(title='La fine', _language='it'))['_id']
    book = db.get_book_by_id(id)['_source']
    del(book['title'])
    book['author'] = 'author_one'
    db.modify_book(id, book)
    mod_book = db.get_book_by_id(id)['_source']
    ok_('title' not in mod_book)
    eq_(mod_book['author'], 'author_one')

@with_setup(cleanall, cleanall)
def test_modify_book_fts_correct():
    id = db.add_book(body=dict(title='La fine', _language='it'))['_id']
    book = db.get_book_by_id(id)
    del(book['_source']['title'])
    book['_source']['author'] = 'Sally Niser'
    db.modify_book(id, book['_source'])
    mod_book = db.get_book_by_id(id)['_source']
    ok_('fine' not in mod_book['_text_it'])
    ok_('Niser' in mod_book['_text_it'])

@with_setup(cleanall, cleanall)
def test_modify_book_version_check():
    id = db.add_book(body=dict(title='La fine', _language='it'))['_id']
    book = db.get_book_by_id(id)
    del(book['_source']['title'])
    book['_source']['author'] = 'author_one'
    db.modify_book(id, book['_source'], version=book['_version'])
    mod_book = db.get_book_by_id(id)['_source']
    ok_('title' not in mod_book)
    eq_(mod_book['author'], 'author_one')

@raises(ConflictError)
@with_setup(cleanall, cleanall)
def test_modify_book_wrong_version():
    id = db.add_book(body=dict(title='La fine', _language='it'))['_id']
    book = db.get_book_by_id(id)
    del(book['_source']['title'])
    book['_source']['author'] = 'author_one'
    db.modify_book(id, book['_source'], version=(book['_version']+1))
    mod_book = db.get_book_by_id(id)['_source']
    ok_('title' not in mod_book)
    eq_(mod_book['author'], 'author_one')
