import sys
sys.path.append('..')
sys.path.append('../..')
from elasticsearch import Elasticsearch

from libreantdb import api, DB

es = Elasticsearch()
db = DB(es, index_name='test-book')


def setUpPackage():
    db.setup_db()


def tearDownPackage():
    if es.indices.exists('test-book'):
        es.indices.delete('test-book')


def cleanall():
    if db.es.indices.exists(db.index_name):
        db.es.delete_by_query(index=db.index_name,
                              body={'query': {'match_all': {}}})
        db.es.indices.delete(index=db.index_name)
    db.setup_db()
    db.es.indices.refresh(index=db.index_name)
