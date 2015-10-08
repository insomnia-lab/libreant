from users import User, db
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


class NotFoundException(Exception):
    pass


class ConflictException(Exception):
    pass
