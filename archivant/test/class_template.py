from archivant import Archivant
from elasticsearch import Elasticsearch
from tempfile import mkdtemp, mkstemp
from shutil import rmtree
import random
import os
import string


class TestArchivant():

    TEST_ES_INDEX = 'test-archivant'
    FSDB_PATH_PREFIX = "archivant_test_"

    @classmethod
    def setUpClass(self):
        self.es = Elasticsearch()

    @classmethod
    def tearDownClass(self):
        self.es.indices.delete(self.TEST_ES_INDEX)

    def setUp(self):
        self.tmpDir = mkdtemp(prefix=self.FSDB_PATH_PREFIX)
        conf = {'ES_INDEXNAME': self.TEST_ES_INDEX,
                'FSDB_PATH': self.tmpDir}
        self.arc = Archivant(conf)

    def tearDown(self):
        self.es.delete_by_query(index=self.TEST_ES_INDEX,
                                body={'query': {'match_all': {}}})
        rmtree(self.tmpDir)
        self.tmpDir = None
        self.arc = None

    @staticmethod
    def generate_volume_metadata():
        return {'_language': 'en',
                'key1': 'value1',
                'key2': {'key21': 'value21', 'key22': 'value22'},
                'key3': [1, 2, 3]}

    @staticmethod
    def random_string(length):
        return ''.join(random.choice(string.hexdigits) for _ in range(length))

    def generate_file(self):
        fd, path = mkstemp(dir=self.tmpDir)
        with os.fdopen(fd, 'wb') as f:
            f.write(self.random_string(10))
        return path

    def generate_attachments(self, n):
        files = []
        for i in range(0, n):
            files.append({'file': self.generate_file()})
        return files
