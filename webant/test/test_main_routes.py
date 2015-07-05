from webant import create_app
from conf.defaults import get_def_conf
from nose.tools import eq_


def get_wtc():
    return create_app(get_def_conf()).test_client()


def test_home():
    wtc = get_wtc()
    eq_(wtc.get('/').status_code, 200)


def test_get_add():
    wtc = get_wtc()
    eq_(wtc.get('/add').status_code, 200)


def test_empty_search():
    wtc = get_wtc()
    eq_(wtc.get('/search?q=*').status_code, 200)


def test_descr():
    wtc = get_wtc()
    eq_(wtc.get('/description.xml').status_code, 200)


def test_recents():
    wtc = get_wtc()
    eq_(wtc.get('/recents').status_code, 200)
