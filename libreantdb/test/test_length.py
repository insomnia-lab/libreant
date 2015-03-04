'''
This module will connect to your elasticsearch instance.
An index will be reserved to the tests.
'''
from __future__ import print_function

from nose.tools import eq_, with_setup

from . import db, cleanall


@with_setup(cleanall, cleanall)
def test_no_elements():
    eq_(len(db), 0)


@with_setup(cleanall, cleanall)
def test_one_element():
    eq_(len(db), 0)
    db.add_book(doc_type='book',
                body=dict(title='Un libro', _language='it'))
    db.es.indices.refresh(index=db.index_name)
    eq_(len(db), 1)
