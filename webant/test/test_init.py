from webant import create_app
from conf.defaults import get_def_conf


def test_init_no_conf():
    webant = create_app()


def test_init_def_conf():
    webant = create_app(get_def_conf())

def test_init_debug():
    c = get_def_conf()
    c.update(dict(DEFAULT=True))
    webant = create_app(c)
