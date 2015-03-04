from nose.tools import eq_, with_setup, ok_
from . import db, cleanall

@with_setup(cleanall, cleanall)
def test_last():
    '''
    test if last_inserted follow the insertion order
    '''
    num = 4
    ids = []
    for i in range(0,num):
        ids.append(db.add_book(doc_type='book',
                   body=dict(title='ma che ne so {}'.format(i), _language='it'))['_id'])
    db.es.indices.refresh(index=db.index_name)
    hits = db.get_last_inserted()['hits']['hits']
    eq_(len(hits), num)
    for hit, id in zip(hits, reversed(ids)):
        eq_(hit['_id'], id)

@with_setup(cleanall, cleanall)
def test_has_timestamp():
    ''' last_inserted results must have ['fields']['_timestamp']'''
    id = db.add_book(doc_type='book',
                     body=dict(title='ma che ne so', _language='it'))['_id']
    db.es.indices.refresh(index=db.index_name)
    assert('_timestamp' in db.get_last_inserted()['hits']['hits'][0]['fields'])
