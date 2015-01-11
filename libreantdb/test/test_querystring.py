from __future__ import print_function

from nose.tools import eq_, with_setup

from . import db, cleanall


@with_setup(cleanall, cleanall)
def test_noquotes():
    '''Quoting means "exact portion of text"'''
    b = dict(title='Manifesto del partito comunista',
             actors=['Karl Marx', 'Friedrich Engels'],
             _language='it')
    db.add_book(doc_type='book', body=b)
    db.es.indices.refresh(index=db.index_name)
    res = db.user_search('manifesto comunista')['hits']
    eq_(res['total'], 1)
    res = db.user_search('"manifesto comunista"')['hits']
    eq_(res['total'], 0)
    res = db.user_search('"manifesto del partito comunista"')['hits']
    eq_(res['total'], 1)
    res = db.user_search('"manifesto del partito"')['hits']
    eq_(res['total'], 1)
    res = db.user_search('"partito comunista"')['hits']
    eq_(res['total'], 1)


@with_setup(cleanall, cleanall)
def test_field():
    '''Query string support field:value'''
    b = dict(title='Manifesto del partito comunista',
             actors=['Karl Marx', 'Friedrich Engels'],
             _language='it')
    bookid1 = db.add_book(doc_type='book', body=b)['_id']
    b = dict(title='Viva Marx',
             actors=['Topo gigio', 'paolino paperino'],
             _language='it')
    bookid2 = db.add_book(doc_type='book', body=b)['_id']
    db.es.indices.refresh(index=db.index_name)

    eq_(db.get_all_books()['hits']['total'], 2)
    res = db.user_search('marx')['hits']
    eq_(res['total'], 2)

    res = db.user_search('actors:marx')['hits']
    eq_(res['total'], 1)
    eq_(res['hits'][0]['_id'], bookid1)

    res = db.user_search('title:marx')['hits']
    eq_(res['total'], 1)
    eq_(res['hits'][0]['_id'], bookid2)


@with_setup(cleanall, cleanall)
def test_quotedfield():
    '''Query string support field:"test phrase"'''
    b = dict(title='Manifesto del partito comunista',
             actors=['Karl Marx', 'Friedrich Engels'],
             _language='it')
    bookid1 = db.add_book(doc_type='book', body=b)['_id']
    b = dict(title='La guerra lampo dei fratelli Marx',
             actors=['Groucho Marx', 'Zeppo Marx'],
             _language='it')
    db.add_book(doc_type='book', body=b)['_id']
    db.es.indices.refresh(index=db.index_name)

    res = db.user_search('actors:marx')['hits']
    eq_(res['total'], 2)

    res = db.user_search('actors:"karl marx"')['hits']
    eq_(res['total'], 1)
    eq_(res['hits'][0]['_id'], bookid1)
