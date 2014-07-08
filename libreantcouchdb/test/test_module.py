import sys
sys.path.append('..')

from nose.tools import eq_


def test_setup():
    '''just setup'''
    import libreantcouchdb as libreantdb
    libreantdb.setup(3, viewsetup=False)


def test_setup_get():
    '''get_db is coherent with setup'''
    import libreantcouchdb as libreantdb
    libreantdb.setup(3, viewsetup=False)
    eq_(libreantdb.get_db(), 3)

def test_modules():
    '''Test which modules are present'''
    import libreantcouchdb as libreantdb
    hasattr(libreantdb, 'models')
    hasattr(libreantdb, 'views')
