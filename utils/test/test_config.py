'''
This tests are about the configuration system.

Extensive use of the 'environ' variable is made: this is in order to simulate
the environment without going into heavy mocking.
'''
from tempfile import mkstemp
import json
import os

from nose.tools import eq_, raises

from utils.config_utils import from_envvars, from_envvar_file


@raises(RuntimeError)
def test_needs_prefix_or_envvars():
    '''without providing prefix nor envvars, you got failure'''
    from_envvars()


def test_empty():
    '''no environment means no conf'''
    conf = from_envvars(prefix='WEBANT_', environ={})
    eq_(conf, {})


def test_no_matching_prefix():
    '''no matching environment variable means no conf'''
    conf = from_envvars(prefix='WEBANT_', environ={'OTHERPREFIX_OPT': 3})
    eq_(conf, {})


def test_simplestring():
    conf = from_envvars(prefix='WEBANT_', environ={'WEBANT_FOO': 'bar'})
    eq_(len(conf), 1)
    eq_(conf['FOO'], 'bar')


def test_list_json():
    conf = from_envvars(prefix='WEBANT_',
                        environ={'WEBANT_FOO': '["bar", "foo", 42]'})
    eq_(len(conf), 1)
    foo = conf.get('FOO')
    eq_(type(foo), list)
    eq_(len(foo), 3)
    eq_(foo[0], 'bar')
    eq_(foo[2], 42)


def test_list_json_disabled():
    '''if as_json is False, there is no value parsing'''
    conf = from_envvars(prefix='WEBANT_',
                        environ={'WEBANT_FOO': '["bar", "foo", 42]'},
                        as_json=False)
    eq_(len(conf), 1)
    foo = conf.get('FOO')
    eq_(type(foo), str)
    eq_(foo, '["bar", "foo", 42]')


def test_envvars_list():
    '''envvars allows to manually specify which variables to use'''
    conf = from_envvars(envvars=['BAZ'],
                        environ={'BAZ': 'yeah', 'unused': 42},
                        as_json=False)
    eq_(len(conf), 1)
    eq_(conf['BAZ'], 'yeah')


def test_envvars_dict():
    '''if envvars is a dict, it can "remap" options'''
    conf = from_envvars(envvars={'BAZ': 'NEWNAME'},
                        environ={'BAZ': 'yeah', 'unused': 42},
                        as_json=False)
    eq_(len(conf), 1)
    eq_(conf['NEWNAME'], 'yeah')


def test_envvars_nonexisting():
    '''envvars can contain non-existing options; they will be skipped'''
    conf = from_envvars(envvars=['BAZ', 'nonexistent'],
                        environ={'BAZ': 'yeah', 'unused': 42},
                        as_json=False)
    eq_(len(conf), 1)
    eq_(conf['BAZ'], 'yeah')


def test_file_variable_notset():
    '''if config file variable is not set, we just ignore it'''
    conf = from_envvar_file('MYRC', environ={})
    eq_(conf, {})


def test_file_notexist():
    '''if config file does not exist, it is ignored'''
    conf = from_envvar_file('MYRC',
                            environ={'MYRC': '/tmp/notexist.webant.test'})
    eq_(conf, {})


def test_file_exist():
    '''if config file exists, it is parsed as json'''
    tempfd, temppath = mkstemp(suffix='.json', prefix='webant_test',
                               text=True)
    try:
        tempbuf = os.fdopen(tempfd, 'w')
        tempbuf.write(json.dumps(dict(FOO='baz', MEANING=42)))
        tempbuf.close()

        conf = from_envvar_file('MYRC',
                                environ={'MYRC': temppath})
        eq_(len(conf), 2)
        eq_(conf['FOO'], 'baz')
        eq_(conf['MEANING'], 42)
    finally:
        os.unlink(temppath)
