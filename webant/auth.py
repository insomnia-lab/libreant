from flask import session
from users.api import get_user, get_anonymous_user, NotFoundException
from authbone import Authenticator, Authorizator


class AuthtFromSession(Authenticator):

    USERID_KEY = 'user_id'

    def login(self, userID):
        session[self.USERID_KEY] = userID

    def logout(self):
        session.pop(self.USERID_KEY)

    def is_logged_in(self):
        return self.USERID_KEY in session

    def auth_data_getter(self):
        return session.get(self.USERID_KEY, None)

    def authenticate(self, userID):
        try:
            return get_user(id=userID)
        except NotFoundException:
            return None


class AuthtFromSessionAnon(AuthtFromSession):

    def bad_auth_data_callback(self):
        self.identity_elaborator(get_anonymous_user())

    def not_authenticated_callback(self):
        self.identity_elaborator(get_anonymous_user())


class AuthzFromSession(Authorizator):

    def check_capability(self, identity, capability):
        return identity.can(capability[0], capability[1])


class TransparentAutht(AuthtFromSession):

    def perform_authentication(self, *args, **kwargs):
        pass


class TransparentAuthz(AuthzFromSession):

    def perform_authorization(self, *args, **kwargs):
        pass
