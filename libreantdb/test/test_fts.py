'''
This module will connect to your elasticsearch instance.
An index will be reserved to the tests.
'''
from __future__ import print_function
from pprint import pprint

from nose.tools import eq_, with_setup

from . import db, cleanall


@with_setup(cleanall, cleanall)
def test_fts_basic():
    '''Simple fts, without stemming or anything fancy'''
    db.add_book(doc_type='book',
                body=dict(title='La fine', language='it'))
    db.add_book(doc_type='book',
                body=dict(title="It's fine", language='en'))
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_simplequery('fine')
    eq_(res['hits']['total'], 2)


@with_setup(cleanall, cleanall)
def test_fts_it_plural_manual():
    '''
    FTS with Italian plurals; explicitly querying on the language

    This test is strictly simpler that test_fts_it_plural
    '''
    title = "La donna nella russia di pietro"
    query = 'donne'
    db.add_book(doc_type='book', body=dict(title=title, language='it'))
    for phrase in title, query:
        pprint(db.es.indices.analyze(index=db.index_name,
                                     body=phrase,
                                     analyzer='it_analyzer')['tokens'])
    db.es.indices.refresh(index=db.index_name)

    res = db._search(db._get_search_field('text_it', query))
    eq_(res['hits']['total'], 1)


@with_setup(cleanall, cleanall)
def test_fts_it_plural():
    '''FTS with Italian plurals'''
    title = "La donna nella russia di pietro"
    query = 'donne'
    wrong_query = 'donato'
    db.add_book(doc_type='book', body=dict(title=title, language='it'))
    for phrase in title, query:
        pprint(db.es.indices.analyze(index=db.index_name,
                                     body=phrase,
                                     analyzer='it_analyzer')['tokens'])
    db.es.indices.refresh(index=db.index_name)

    res = db.get_books_multilanguage(query)
    eq_(res['hits']['total'], 1)
    res = db.get_books_multilanguage(wrong_query)
    eq_(res['hits']['total'], 0)


@with_setup(cleanall, cleanall)
def test_fts_en_manual():
    '''FTS with English; manually specifying the language'''
    title = 'Living with cats'
    query = 'live'
    wrong_query = 'love'
    db.add_book(doc_type='book', body=dict(title=title, language='en'))
    for phrase in title, query, wrong_query:
        pprint(db.es.indices.analyze(index=db.index_name,
                                     body=phrase,
                                     analyzer='english')['tokens'])
    db.es.indices.refresh(index=db.index_name)
    res = db._search(db._get_search_field('text_en', 'living'))
    eq_(res['hits']['total'], 1)
    res = db._search(db._get_search_field('text_en', wrong_query))
    eq_(res['hits']['total'], 0)
    res = db._search(db._get_search_field('text_en', query))
    eq_(res['hits']['total'], 1)


@with_setup(cleanall, cleanall)
def test_fts_en_verbs():
    '''FTS with English verbs. Automatic language "detection"'''
    title = 'Living with cats'
    query = 'live'
    wrong_query = 'love'
    db.add_book(doc_type='book', body=dict(title=title, language='en'))
    for phrase in title, query, wrong_query:
        pprint(db.es.indices.analyze(index=db.index_name,
                                     body=phrase,
                                     analyzer='english')['tokens'])
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_multilanguage('living')
    eq_(res['hits']['total'], 1)
    res = db.get_books_multilanguage(wrong_query)
    eq_(res['hits']['total'], 0)
    res = db.get_books_multilanguage(query)
    eq_(res['hits']['total'], 1)


@with_setup(cleanall, cleanall)
def test_fts_en_plural():
    '''FTS with English plurals'''
    title = 'Bugs are not ok, with unit testing'
    query = 'bug'
    wrong_query = 'buggy'
    db.add_book(doc_type='book', body=dict(title=title, language='en'))
    for phrase in title, query, wrong_query:
        pprint(db.es.indices.analyze(index=db.index_name,
                                     body=phrase,
                                     analyzer='english')['tokens'])
    db.es.indices.refresh(index=db.index_name)
    res = db.get_books_multilanguage('bugs')
    eq_(res['hits']['total'], 1)
    res = db.get_books_multilanguage(wrong_query)
    eq_(res['hits']['total'], 0)
    res = db.get_books_multilanguage(query)
    eq_(res['hits']['total'], 1)
