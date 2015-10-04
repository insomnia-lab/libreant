from . import TestBaseClass
from peewee import IntegrityError
from nose.tools import eq_, ok_
from users import User


class TestUsers(TestBaseClass):

    def test_user_creation(self):
        newUser = User.create(name='test', password='pass')
        User.get(User.name == newUser.name)
        eq_(User.select().count(), 1)

    def test_user_removal(self):
        newUser = User.create(name='test', password='pass')
        newUser.delete_instance()
        eq_(User.select().count(), 0)

    def test_user_unique_name(self):
        User.create(name='test', password='pass')
        with self.assertRaises(IntegrityError):
            User.create(name='test', password='plusPass')

    def test_user_verify_right_password(self):
        User.create(name='test', password='right_pass')
        ok_(User.get(User.name == 'test').verify_password('right_pass'))

    def test_user_verify_wrong_password(self):
        User.create(name='test', password='pass')
        ok_(not User.get(User.name == 'test').verify_password('wrong_pass'))

    def test_user_change_password(self):
        u = User.create(name='test', password='pass_1')
        u = User.get(User.name == 'test')
        u.set_password('pass_2')
        u.save()
        u = User.get(User.name == 'test')
        ok_(not u.verify_password('pass_1'))
        ok_(u.verify_password('pass_2'))
