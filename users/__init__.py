from peewee import SqliteDatabase
from playhouse import db_url
from passlib.context import CryptContext
from models import db_proxy,\
    User, Group, UserToGroup, GroupToCapability, Capability


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
        * sqlite: `sqlite:///my_database.db`
        * postgres: `postgresql://postgres:my_password@localhost:5432/my_database`
        * mysql: `mysql://user:passwd@ip:port/my_db`
    '''
    if not dbURL:
        dbURL = 'sqlite:///:memory:'
    db_proxy.initialize(db_url.connect(dbURL))
    return db_proxy


def create_tables(database):
    '''Create all tables in the given database'''
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
    if User.select().where(User.name == 'admin').exists():
        return
    admin = User.create(name='admin', password='admin')
    admins = Group.create(name='admins')
    starCap = Capability.create(domain='.+',
                                action=(Capability.CREATE |
                                        Capability.READ |
                                        Capability.UPDATE |
                                        Capability.DELETE))
    admins.capabilities.add(starCap)
    admin.groups.add(admins)
    admin.save()


def init_db(dbURL, pwd_salt_size=None, pwd_rounds=None):
    '''Initialize users database

    initialize database and create necessary tables
    to handle users oprations.

    :param dbURL: database url, as described in :func:`init_proxy`
    '''
    db = init_proxy(dbURL)
    global pwdCryptCtx
    pwdCryptCtx = gen_crypt_context(salt_size=pwd_salt_size, rounds=pwd_rounds)
    create_tables(db)
    return db


def gen_crypt_context(salt_size=None, rounds=None):
    return CryptContext(schemes=['pbkdf2_sha256', 'pbkdf2_sha512'],
                        default='pbkdf2_sha256',
                        all__salt_size=salt_size,
                        all__default_rounds=rounds)
