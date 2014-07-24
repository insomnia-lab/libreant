import sys
sys.path.append('..')
sys.path.append('../..')
from elasticsearch import Elasticsearch

from libreantdb import api, DB

es = Elasticsearch()
db = DB(es)
db.index_name = 'test-book'


def setUpPackage():
    db.setup_db()


def tearDownPackage():
    es.indices.delete('test-book')


def cleanall():
    db.es.delete_by_query(index=db.index_name,
                          body={'query': {'match_all': {}}})
    db.es.indices.refresh(index=db.index_name)
