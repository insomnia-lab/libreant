'''
This module will connect to your elasticsearch instance.
An index will be reserved to the tests.
'''

from nose.tools import ok_, eq_, with_setup

from . import db, cleanall


@with_setup(cleanall, cleanall)
def test_iterate_all():
    n = 5
    ids = list()
    for i in range(n):
        id = db.add_book(body=dict(num=i, title='Un libro', _language='it'))['_id']
        ids.append(id)
    db.es.indices.refresh(index=db.index_name)
    ret_ids = [b['_id'] for b in db.iterate_all()]
    eq_(len(set(ids).symmetric_difference(ret_ids)), 0)


@with_setup(cleanall, cleanall)
def test_iterate_all_empty():
    eq_(len([b for b in db.iterate_all()]), 0)


@with_setup(cleanall, cleanall)
def test_iterate_all_disturbed():
    '''if you add elements after the iteration query
       they should not compare in the results
    '''
    n = 5
    ids = list()
    for i in range(n):
        id = db.add_book(body=dict(num=i, title='Un libro', _language='it'))['_id']
        ids.append(id)
    db.es.indices.refresh(index=db.index_name)
    books = list()
    for b in db.iterate_all():
        db.add_book(body=dict(title='Un libro', _language='it'))
        books.append(b)
    ret_ids = [ b['_id'] for b in books]
    eq_(len(set(ids).symmetric_difference(ret_ids)), 0)
