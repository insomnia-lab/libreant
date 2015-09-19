import re
from peewee import PrimaryKeyField, CharField, ForeignKeyField, IntegerField,\
    Model, Proxy
from playhouse.fields import ManyToManyField
import users

# Create a proxy to DB that can
# be instantiated at runtime
db_proxy = Proxy()

GroupToCapabilityProxy = Proxy()
UserToGroupProxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = db_proxy  # Use proxy for our DB.


class Capability(BaseModel):
    """Capability model

    A capability is composed by a :attr:`domain`
    and an :attr:`action`. It represent the possibility
    to perform a specific set of actions on the resources
    described by the domain

    :attr:`domain` is a regular expression that
        describe all the resources involved in the capability.
        You can use :func:`simToReg` and :func:`regToSim` utility function
        to easily manipulate domain regular expressions.
    :attr:`action` is a bitmask representing
        the actions involved in the capability
        you can compose the bitmask by using the following class
        constants:
        * CREATE (C)
        * READ (R)
        * UPDATE (U)
        * DELETE (D)
    """
    CREATE = C = 2**3
    READ = R = 2**2
    UPDATE = U = 2**1
    DELETE = D = 2**0

    domain = CharField()
    action = IntegerField()

    class Meta:
        indexes = ((('domain', 'action'), True),)

    @classmethod
    def simToReg(self, sim):
        """Convert simplified domain expression to regular expression"""
        # remove initial slash if present
        res = re.sub('^/', '', sim)
        res = re.sub('/$', '', res)
        return '^/?' + re.sub('\*', '[^/]+', res) + '/?$'

    @classmethod
    def regToSim(self, reg):
        """Convert regular expression to simplified domain expression"""
        return re.sub('\[\^/\]\+', '*', reg[3:-3])

    def match_domain(self, dom):
        """Check if the given :param:`dom` is included in this capability domain"""
        return bool(re.match(self.domain, dom))

    def match_action(self, act):
        """Check if the given :param:`act` is allowed from this capability"""
        return (self.action & act) == act

    def match(self, dom, act):
        """Check if the given :param:`domain` and :param:`act` are allowed
        by this capability"""
        return self.match_domain(dom) and self.match_action(act)


class Group(BaseModel):
    """Group model

    A group has a set of capabilities and a
    number of users belonging to it.
    It's an handy way of grouping users with the same capability.
    """
    id = PrimaryKeyField()
    name = CharField(unique=True)
    capabilities = ManyToManyField(Capability, related_name='groups', through_model=GroupToCapabilityProxy)

    def can(self, domain, action):
        for cap in self.capabilities:
            if(cap.match(domain, action)):
                return True
        return False


class User(BaseModel):
    """User model"""
    id = PrimaryKeyField()
    name = CharField(unique=True)
    pwd_hash = CharField(max_length=255, null=True)
    groups = ManyToManyField(Group, related_name='users', through_model=UserToGroupProxy)

    def __init__(self, **kargs):
        super(User, self).__init__()
        if 'name' in kargs:
            self.name = kargs['name']
        if 'password' in kargs:
            self.set_password(kargs['password'])

    def set_password(self, password):
        """set user password

        Generate random salt, derivate the given password using pbkdf2
        algorith and store a summarizing string in :attr:`pwd_hash`.
        For hash format refer to `passlib documentation <https://pythonhosted.org/passlib/lib/passlib.hash.pbkdf2_digest.html#format-algorithm>`_.
        """
        self.pwd_hash = users.pwdCryptCtx.encrypt(password)

    def verify_password(self, password):
        """Check if the given password is the same
        stored for this user"""
        return users.pwdCryptCtx.verify(password, self.pwd_hash)

    @property
    def capabilities(self):
        return (Capability
                .select()
                .join(GroupToCapability).join(Group)
                .join(UserToGroup).join(User)
                .where(User.id == self.id))

    def can(self, domain, action):
        """Can perform :param:`action` on the given :param:`domain`."""
        for cap in self.capabilities:
            if(cap.match(domain, action)):
                return True
        return False


class GroupToCapability(BaseModel):
    group = ForeignKeyField(Group, on_delete='CASCADE')
    capability = ForeignKeyField(Capability, on_delete='CASCADE')


class UserToGroup(BaseModel):
    user = ForeignKeyField(User, on_delete='CASCADE')
    group = ForeignKeyField(Group, on_delete='CASCADE')


GroupToCapabilityProxy.initialize(GroupToCapability)
UserToGroupProxy.initialize(UserToGroup)
