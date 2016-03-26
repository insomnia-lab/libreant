from . import WebantTestCase
from nose.tools import eq_


class WebantMainRoutes(WebantTestCase):

    def test_home(self):
        eq_(self.wtc.get('/').status_code, 200)

    def test_get_add(self):
        eq_(self.wtc.get('/add').status_code, 200)

    def test_empty_search(self):
        eq_(self.wtc.get('/search?q=*').status_code, 200)

    def test_descr(self):
        eq_(self.wtc.get('/description.xml').status_code, 200)

    def test_recents(self):
        eq_(self.wtc.get('/recents').status_code, 200)
