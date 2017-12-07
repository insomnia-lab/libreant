from libreantdb import DB
from utils.es import Elasticsearch


es = Elasticsearch()
db = DB(es, index_name='test-book')


def setUpPackage():
    db.setup_db()


def tearDownPackage():
    if es.indices.exists('test-book'):
        es.indices.delete('test-book')


def cleanall():
    if db.es.indices.exists(db.index_name):
        db.delete_all()
    else:
        db.setup_db()
    db.es.indices.refresh(index=db.index_name)
