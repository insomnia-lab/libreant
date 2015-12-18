'''
The `users` package manages the models and the API about users, groups and
capabilities. Note that this package does **not** specify permissions for
objects. Actual permissions are handled at the UI level.

The main concepts are:

- A :py:class:`~users.models.User` is what you think it is; something that you can login as.
- A :py:class:`~users.models.Group` is a collection of users. Note that a user can belong to multiple
  groups. A group has capabilities.
- A :py:class:`~users.models.Capability` is a "granted permission". You can think of it like a piece of
  paper saying, ie. "you can create new attachments".

  - Its :py:attr:`~users.models.Capability.action` is a composition of Create, Read, Update, Delete
    (it follows the CRUD model).
  - A :py:attr:`~users.models.Capability.domain` is a regular expression that
    must "match" to the description of an object. ie. ``/cars/*`` means "every
    car", while ``/cars/*/tires/`` means "the tires of every car"

This also means that a user has no capability (directly). It just belongs to
groups, which, in turn, have capabilities.

The rationale behind what a Capability is may seem baroque, but there are
several advantages to it:

- it is decoupled from  the actual domains used by the UI
- the regular expression make it possible to create groups that can operate on
  everything (``*``).
'''
from peewee import SqliteDatabase
from playhouse import db_url
from passlib.context import CryptContext
from models import db_proxy,\
    User, Group, UserToGroup, GroupToCapability, Capability, Action
import logging


class SqliteFKDatabase(SqliteDatabase):
    '''SqliteDatabase with foreignkey support enabled'''

    def initialize_connection(self, conn):
        self.execute_sql('PRAGMA foreign_keys=ON;')


# replace default sqlite scheme
# in order to support foreign key
db_url.schemes['sqlite'] = SqliteFKDatabase

# context to be use for password hashing
# it's initialized and configured by
pwdCryptCtx=None

db = db_proxy


def init_proxy(dbURL):
    '''Instantiate proxy to the database

    :param dbURL: the url describing connection parameters
        to the choosen database. The url must have format explained in the `Peewee url documentation
        <http://peewee.readthedocs.org/en/latest/peewee/playhouse.html#db-url>`_.

        examples:
         * sqlite: ``sqlite:///my_database.db``
         * postgres: ``postgresql://postgres:my_password@localhost:5432/my_database``
         * mysql: ``mysql://user:passwd@ip:port/my_db``
    '''
    db_proxy.initialize(db_url.connect(dbURL))
    return db_proxy


def create_tables(database):
    '''Create all tables in the given database'''
    logging.getLogger(__name__).debug("Creating missing database tables")
    database.connect()
    database.create_tables([User,
                            Group,
                            UserToGroup,
                            GroupToCapability,
                            Capability], safe=True)


def populate_with_defaults():
    '''Create user admin and grant him all permission

    If the admin user already exists the function will simply return
    '''
    logging.getLogger(__name__).debug("Populating with default users")
    if not User.select().where(User.name == 'admin').exists():
        admin = User.create(name='admin', password='admin')
        admins = Group.create(name='admins')
        starCap = Capability.create(domain='.+',
                                    action=(Action.CREATE |
                                            Action.READ |
                                            Action.UPDATE |
                                            Action.DELETE))
        admins.capabilities.add(starCap)
        admin.groups.add(admins)
        admin.save()
    if not User.select().where(User.name == 'anonymous').exists():
        anon = User.create(name='anonymous', password='')
        anons = Group.create(name='anonymous')
        anon.groups.add(anons)
        anon.save()


def init_db(dbURL, pwd_salt_size=None, pwd_rounds=None):
    '''Initialize users database

    initialize database and create necessary tables
    to handle users oprations.

    :param dbURL: database url, as described in :func:`init_proxy`
    '''
    if not dbURL:
        dbURL = 'sqlite:///:memory:'
    logging.getLogger(__name__).debug("Initializing database: {}".format(dict(url=dbURL,
                                                                              pwd_salt_size=pwd_salt_size,
                                                                              pwd_rounds=pwd_rounds)))
    try:
        db = init_proxy(dbURL)
        global pwdCryptCtx
        pwdCryptCtx = gen_crypt_context(salt_size=pwd_salt_size, rounds=pwd_rounds)
        create_tables(db)
        return db
    except Exception as e:
        e.args = (e.args[0] + ' [users database]',)
        raise


def gen_crypt_context(salt_size=None, rounds=None):
    return CryptContext(schemes=['pbkdf2_sha256', 'pbkdf2_sha512'],
                        default='pbkdf2_sha256',
                        all__salt_size=salt_size,
                        all__default_rounds=rounds)
