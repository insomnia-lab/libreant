from webant.test import WebantTestCase
from nose.tools import eq_


class TestApiArchivant(WebantTestCase):

    API_PREFIX = '/api/v1'

    def test_get_volumes(self):
        eq_(self.wtc.get(self.API_PREFIX + '/volumes/').status_code, 200)
