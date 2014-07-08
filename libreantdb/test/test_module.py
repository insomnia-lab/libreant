import sys
sys.path.append('..')

from nose.tools import eq_


def test_setup():
    '''just setup'''
    import libreantdb
    libreantdb.setup(3)


def test_setup_get():
    '''get_db is coherent with setup'''
    import libreantdb
    libreantdb.setup(3)
    eq_(libreantdb.get_db(), 3)

def test_modules():
    '''Test which modules are present'''
    import libreantdb
    hasattr(libreantdb, 'models')
    hasattr(libreantdb, 'views')
