from . import TestBaseClass
from nose.tools import eq_
from users import User, Group, UserToGroup
from peewee import IntegrityError


class TestGroup(TestBaseClass):

    def test_group_creation(self):
        newGroup = Group.create(name='chefs')
        Group.get(Group.name == newGroup.name)
        eq_(Group.select().count(), 1)

    def test_group_unique_name(self):
        Group.create(name='cyclists')
        with self.assertRaises(IntegrityError):
            Group.create(name='cyclists')

    def test_assign_user_to_group(self):
        anons = Group.create(name='anons')
        jhondohe = User.create(name='jhondhoe', password='pass')
        anons.users.add(jhondohe)
        anons.save()
        eq_(jhondohe.groups.count(), 1)
        eq_(jhondohe.groups.get().id, anons.id)

    def test_assign_duplicate_user_to_group(self):
        anons = Group.create(name='anons')
        jhondohe = User.create(name='jhondhoe', password='pass')
        anons.users.add(jhondohe)
        anons.save()
        with self.assertRaises(IntegrityError):
            anons.users.add(jhondohe)
            anons.save()
        eq_(jhondohe.groups.count(), 1)
        eq_(jhondohe.groups.get().id, anons.id)

    def test_remove_user_from_group(self):
        anons = Group.create(name='anons')
        jhondohe = User.create(name='jhondhoe', password='pass')
        anons.users.add(jhondohe)
        anons.save()
        anons.users.remove(jhondohe)
        anons.save()
        eq_(jhondohe.groups.count(), 0)
        eq_(UserToGroup.select().count(), 0)

    def test_assign_user_to_multiple_group(self):
        rebels = Group.create(name='rebels')
        aliens = Group.create(name='aliens')
        allGroups = [aliens, rebels]
        # https://en.wikipedia.org/wiki/They_Live
        user = User.create(name='doubtful')
        user.groups.add(allGroups)
        belongsID = [g.id for g in user.groups]
        allGroupsID = [g.id for g in allGroups]
        eq_((set(belongsID), len(belongsID)), (set(allGroupsID), len(allGroupsID)))
