import unittest
from elasticsearch import Elasticsearch

from webant import create_app
from conf.defaults import get_def_conf


class WebantTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        conf = get_def_conf()
        conf.update({
            'TESTING': True,
            'ES_INDEXNAME': 'webant_test',
        })
        cls.conf = conf

    @classmethod
    def tearDownClass(cls):
        es = Elasticsearch()
        es.indices.delete(cls.conf['ES_INDEXNAME'], ignore=[404])

    def setUp(self):
        self.wtc = create_app(self.conf).test_client()

    def tearDown(self):
        del self.wtc


class WebantUsersTestCase(WebantTestCase):

    @classmethod
    def setUpClass(cls):
        super(WebantUsersTestCase, cls).setUpClass()
        cls.conf.update({
             'PWD_ROUNDS': 1,
             'USERS_DATABASE': 'sqlite:///:memory:'
        })
