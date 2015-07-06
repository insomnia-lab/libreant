from archivant import Archivant
from archivant.exceptions import FileOpNotSupported
from tempfile import mkdtemp
from shutil import rmtree
from elasticsearch import Elasticsearch, ElasticsearchException
from nose.tools import raises


TEST_ES_INDEX = 'test-archivant'
FSDB_PATH_PREFIX = "archivant_test_"


def cleanup(esIndex=None, tmpDir=None):
    if esIndex is not None:
        es = Elasticsearch()
        if es.indices.exists(esIndex):
            es.indices.delete(esIndex)

    if tmpDir is not None:
        rmtree(tmpDir)


def test_instantiation_ok():
    tmpDir = mkdtemp(prefix=FSDB_PATH_PREFIX)
    conf = {'ES_INDEXNAME': TEST_ES_INDEX,
            'FSDB_PATH': tmpDir}
    Archivant(conf)
    cleanup(esIndex=TEST_ES_INDEX, tmpDir=tmpDir)


@raises(FileOpNotSupported)
def test_instantiation_no_fsdb():
    conf = {'ES_INDEXNAME': TEST_ES_INDEX}
    arc = Archivant(conf)
    arc._fsdb


@raises(ValueError)
def test_instantiation_no_indexname():
    tmpDir = mkdtemp(prefix=FSDB_PATH_PREFIX)
    conf = {'FSDB_PATH': tmpDir}
    try:
        Archivant(conf)
    finally:
        cleanup(tmpDir=tmpDir)


def test_instantiation_hosts_error():
    '''this should not raise errors'''
    tmpDir = mkdtemp(prefix=FSDB_PATH_PREFIX)
    conf = {'ES_INDEXNAME': TEST_ES_INDEX,
            'ES_HOSTS': "127.0.0.1:12345",
            'FSDB_PATH': tmpDir}
    try:
        Archivant(conf)
    finally:
        cleanup(tmpDir=tmpDir)


@raises(ElasticsearchException)
def test_instantiation_hosts_error_on_query():
    '''explicitly doing queries will raise error'''
    tmpDir = mkdtemp(prefix=FSDB_PATH_PREFIX)
    conf = {'ES_INDEXNAME': TEST_ES_INDEX,
            'ES_HOSTS': "127.0.0.1:12345",
            'FSDB_PATH': tmpDir}
    try:
        arc = Archivant(conf)
        arc.get_volume('whatever')
    finally:
        cleanup(tmpDir=tmpDir)
