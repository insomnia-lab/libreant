from users import User, Group, db
from peewee import IntegrityError


def add_user(name, password):
    try:
        return User.create(name=name, password=password)
    except IntegrityError:
        raise ConflictException("user with the same name already exists")


def delete_user(id):
    if not User.delete().where(User.id == id).execute():
        raise NotFoundException('no user could be found with this id')


def update_user(id, updates):
    with db.atomic():
        u = get_user(id)
        if 'password' in updates:
            u.set_password(updates['password'])
        if 'name' in updates:
            u.name = updates['name']
        u.save()


def get_user(id=None, name=None):
    try:
        if id:
            return User.get(User.id==id)
        elif name:
            return User.get(User.name==name)
        else:
            raise ValueError('nither `id` or `name` was given')
    except User.DoesNotExist:
        raise NotFoundException("no user could be found with these attributes")


def add_group(name):
    try:
        return Group.create(name=name)
    except IntegrityError:
        raise ConflictException("a group with the same name already exists")


def delete_group(id):
    if not Group.delete().where(Group.id == id).execute():
        raise NotFoundException('no group could be found with this id')


def update_group(id, updates):
    with db.atomic():
        g = get_group(id)
        if 'name' in updates:
            g.name = updates['name']
        g.save()


def get_group(id=None, name=None):
    try:
        if id:
            return Group.get(Group.id==id)
        elif name:
            return Group.get(Group.name==name)
        else:
            raise ValueError('nither `id` or `name` was given')
    except Group.DoesNotExist:
        raise NotFoundException("no group could be found with these attributes")


def add_user_to_group(userID, groupID):
    with db.atomic():
        u = get_user(userID)
        g = get_group(groupID)
        u.groups.add(g)
        u.save()


def remove_user_from_group(userID, groupID):
    with db.atomic():
        u = get_user(userID)
        g = get_group(groupID)
        u.groups.remove(g)
        u.save()


def get_groups_of_user(userID):
    for g in get_user(id=userID).groups:
        yield g


def get_users_in_group(groupID):
    for u in get_group(id=groupID).users:
        yield u


class NotFoundException(Exception):
    pass


class ConflictException(Exception):
    pass
