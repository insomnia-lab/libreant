'''
This module will connect to your elasticsearch instance.
An index will be reserved to the tests.
'''

from pprint import pprint

from nose.tools import eq_, with_setup

from . import db, cleanall


@with_setup(cleanall, cleanall)
def test_last_inserted():
    '''Simple fts, without stemming or anything fancy'''
    first = db.add_book( body={ 'order': 'first', '_language':'it'} )
    second = db.add_book( body={ 'order': 'second', '_language':'it'} )
    db.es.indices.refresh(index=db.index_name)
    res = db.get_last_inserted(1)
    pprint(res)
    eq_(res['hits']['hits'][0]['_id'],  second['_id'])
