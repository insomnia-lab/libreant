from users import User, Group, Capability, db
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


def get_capability(capID):
    try:
        return Capability.get(Capability.id == capID)
    except Capability.DoesNotExist:
        raise NotFoundException("no capability could be found with these attributes")


def add_capability(domain, action, simplified=True):
    try:
        if simplified:
           domain = Capability.simToReg(domain)
        return Capability.create(domain=domain, action=action)
    except IntegrityError:
        raise ConflictException("a capability with the same attributes already exists")


def delete_capability(capID):
    if not Capability.delete().where(Capability.id == capID).execute():
        raise NotFoundException('no capability could be found with this id')


def update_capability(id, updates):
    with db.atomic():
        cap = get_capability(id)
        if 'domain' in updates:
            cap.domain = Capability.simToReg(updates['domain'])
        if 'action' in updates:
            cap.action = updates['action']
        cap.save()


def add_capability_to_group(capID, groupID):
    with db.atomic():
        cap = get_capability(capID)
        grp = get_group(groupID)
        grp.capabilities.add(cap)
        cap.save()


def remove_capability_from_group(capID, groupID):
    with db.atomic():
        cap = get_capability(capID)
        grp = get_group(groupID)
        grp.capabilities.remove(cap)
        cap.save()


def get_groups_with_capability(capID):
    for g in get_capability(capID).groups:
        yield g


def get_capabilities_of_group(groupID):
    for c in get_group(groupID).capabilities:
        yield c


def get_anonymous_user():
    return get_user(name='anonymous')


def is_anonymous(user):
    return user.name == 'anonymous'


class NotFoundException(Exception):
    pass


class ConflictException(Exception):
    pass
