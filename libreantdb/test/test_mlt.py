'''
More like this
'''

from __future__ import print_function

from nose.tools import eq_, with_setup

from . import db, cleanall


@with_setup(cleanall, cleanall)
def test_mlt_empty_if_only_one():
    '''
    If there's only one document, mlt is empty
    '''
    book_id = db.add_book(doc_type='book',
                          body=dict(title='La fine', language='it'))['_id']
    db.es.indices.refresh(index=db.index_name)
    eq_(db.mlt(book_id)['hits']['total'], 0)


@with_setup(cleanall, cleanall)
def test_mlt_choose_same():
    '''MLT: There is only one other book, and the name is almost the same'''
    b = dict(title='La fine di tutto',
             actors=['marco', 'giulio'],
             language='it')
    book_id1 = db.add_book(doc_type='book', body=b)['_id']
    b = dict(title='La fine di tutto, o almeno del mondo come lo conosciamo',
             actors=['marco', 'giulio', 'un amico loro'],
             language='it')
    book_id2 = db.add_book(doc_type='book', body=b)['_id']
    assert book_id1 != book_id2
    db.es.indices.refresh(index=db.index_name)
    res = db.mlt(book_id1)['hits']
    eq_(res['total'], 1)
    eq_(res['hits'][0]['_id'], book_id2)
