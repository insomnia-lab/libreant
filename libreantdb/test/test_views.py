import sys
sys.path.append('..')
import libreantdb
# from nose.tools import eq_


def test_general():
    '''Are views working at all?'''
    authors =  list(libreantdb.get_db.view('views/AllAuthors'))
    print authors
    assert authors
