from webant import create_app
from conf.defaults import get_def_conf


def test_init_no_conf():
    create_app()


def test_init_def_conf():
    create_app(get_def_conf())


def test_init_debug():
    c = get_def_conf()
    c.update(dict(DEFAULT=True))
    create_app(c)
