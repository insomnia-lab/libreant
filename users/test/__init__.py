from unittest import TestCase
from users import init_db


class TestBaseClass(TestCase):

    def setUp(self):
        self.udb = init_db('sqlite:///:memory:', pwd_rounds=1)
