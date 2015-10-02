import unittest
from webant import create_app
from conf.defaults import get_def_conf


class WebantTestCase(unittest.TestCase):

    def setUp(self):
        conf = get_def_conf()
        conf['TESTING'] = True
        self.wtc = create_app(conf).test_client()
