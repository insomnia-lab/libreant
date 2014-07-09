import sys
sys.path.append('..')
sys.path.append('../..')
from elasticsearch import Elasticsearch

from libreantdb import DB

es = Elasticsearch()
db = DB(es)
db.index_name = 'test-book'

def setUpPackage():
    db.setup_db()

def tearDownPackage():
    es.indices.delete('test-book')
