import re
from peewee import PrimaryKeyField, CharField, ForeignKeyField, IntegerField,\
    Model, Proxy, CompositeKey
from playhouse.fields import ManyToManyField
import users

# Create a proxy to DB that can
# be instantiated at runtime
db_proxy = Proxy()

GroupToCapabilityProxy = Proxy()
UserToGroupProxy = Proxy()


class ActionField(IntegerField):
    db_field = 'action'

    def db_value(self, value):
        return value

    def python_value(self, value):
        return Action(value)


class BaseModel(Model):
    class Meta:
        database = db_proxy  # Use proxy for our DB.

    def to_dict(self):
        return dict(id=self.id)


class Capability(BaseModel):
    """
    Capability model

    A capability is composed by a :attr:`domain`
    and an :attr:`action`. It represent the possibility
    to perform a specific set of actions on the resources
    described by the domain

    .. py:attribute:: domain

        is a regular expression that describe all the resources involved in the
        capability.  You can use :func:`simToReg` and :func:`regToSim` utility
        function to easily manipulate domain regular expressions.

    .. py:attribute:: action

        an :class:`~users.models.ActionField` *what* can be done on :attr:`domain`
    """

    id = PrimaryKeyField()
    domain = CharField()
    action = ActionField()

    class Meta:
        indexes = ((('domain', 'action'), False),)

    def to_dict(self):
        return dict(id=self.id, domain=self.regToSim(self.domain), action=self.action.to_list())

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
        """Check if the given `dom` is included in this capability domain"""
        return bool(re.match(self.domain, dom))

    def match_action(self, act):
        """Check if the given `act` is allowed from this capability"""
        return (self.action & act) == act

    def match(self, dom, act):
        """
        Check if the given `domain` and `act` are allowed
        by this capability
        """
        return self.match_domain(dom) and self.match_action(act)


class Action(int):
    """Actions utiliy class

    You can use this class attributes to compose the actions bitmask::
        bitmask = Action.CREATE | Action.DELETE

    The following actions are supported:
     - CREATE
     - READ
     - UPDATE
     - DELETE
    """

    # the index of the action in the list correspond to the its position in the bitmask
    ACTIONS = ['CREATE', 'READ', 'UPDATE', 'DELETE']

    def __new__(cls, bitmask):
        if bitmask >= 2**len(cls.ACTIONS):
            raise ValueError('bitmask %d is too big' % bitmask)
        return super(Action, cls).__new__(cls, bitmask)

    def to_list(self):
        '''convert an actions bitmask into a list of action strings'''
        res = []
        for a in self.__class__.ACTIONS:
            aBit = self.__class__.action_bitmask(a)
            if ((self & aBit) == aBit):
                res.append(a)
        return res

    @classmethod
    def from_list(cls, actions):
        '''convert list of actions into the corresponding bitmask'''
        bitmask = 0
        for a in actions:
            bitmask |= cls.action_bitmask(a)
        return Action(bitmask)

    @classmethod
    def action_bitmask(cls, action):
        '''return the bitmask associated withe the given action name'''
        return 2**cls.ACTIONS.index(action.upper())

for i, act in enumerate(Action.ACTIONS):
    setattr(Action, act.upper(), 2**i)


class Group(BaseModel):
    """Group model

    A group has a set of capabilities and a
    number of users belonging to it.
    It's an handy way of grouping users with the same capability.
    """
    id = PrimaryKeyField()
    name = CharField(unique=True)
    capabilities = ManyToManyField(Capability, related_name='groups', through_model=GroupToCapabilityProxy)

    def to_dict(self):
        return dict(id=self.id, name=self.name)

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

    def to_dict(self):
        return dict(id=self.id, name=self.name)

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
        """Can perform `action` on the given `domain`."""
        for cap in self.capabilities:
            if(cap.match(domain, action)):
                return True
        return False


class GroupToCapability(BaseModel):
    group = ForeignKeyField(Group, on_delete='CASCADE')
    capability = ForeignKeyField(Capability, on_delete='CASCADE')

    class Meta:
        primary_key = CompositeKey('group', 'capability')


class UserToGroup(BaseModel):
    user = ForeignKeyField(User, on_delete='CASCADE')
    group = ForeignKeyField(Group, on_delete='CASCADE')

    class Meta:
        primary_key = CompositeKey('user', 'group')


GroupToCapabilityProxy.initialize(GroupToCapability)
UserToGroupProxy.initialize(UserToGroup)
