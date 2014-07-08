_db = None


def get_db():
    global _db
    return _db
from . import models
from . import views


def setup(new_db):
    global _db
    _db = new_db
    views.set_all_views()
