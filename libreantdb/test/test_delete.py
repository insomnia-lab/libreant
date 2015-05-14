from nose.tools import eq_, with_setup, raises
from elasticsearch import NotFoundError
from . import db, cleanall


@with_setup(cleanall, cleanall)
@raises(NotFoundError)
def test_delete_wrong_id():
    db.delete_book("unidacaso")


@with_setup(cleanall, cleanall)
def test_delete_id():
    id = db.add_book(body=dict(title='Un libro', _language='it'))['_id']
    db.delete_book(id)
    db.es.indices.refresh(index=db.index_name)
    eq_(len(db), 0)


@with_setup(cleanall, cleanall)
def test_delete_one_of_two():
    id1 = db.add_book(body=dict(title='Un libro', _language='it'))['_id']
    id2 = db.add_book(body=dict(title='Un libro', _language='it'))['_id']
    db.es.indices.refresh(index=db.index_name)
    eq_(len(db), 2)
    db.delete_book(id2)
    db.es.indices.refresh(index=db.index_name)
    eq_(len(db), 1)
