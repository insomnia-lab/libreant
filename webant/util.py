import functools
from flask import send_file, session
from authbone import Authenticator, Authorizator
from users.api import get_user, get_anonymous_user, NotFoundException


def memoize(obj):
    '''decorator to memoize things'''
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer


def requestedFormat(request,acceptedFormat):
        """Return the response format requested by client

        Client could specify requested format using:
        (options are processed in this order)
            - `format` field in http request
            - `Accept` header in http request
        Example:
            chooseFormat(request, ['text/html','application/json'])
        Args:
            acceptedFormat: list containing all the accepted format
        Returns:
            string: the user requested mime-type (if supported)
        Raises:
            ValueError: if user request a mime-type not supported
        """
        if 'format' in request.args:
            fieldFormat = request.args.get('format')
            if fieldFormat not in acceptedFormat:
                raise ValueError("requested format not supported: "+ fieldFormat)
            return fieldFormat
        else:
            return request.accept_mimetypes.best_match(acceptedFormat)


def send_attachment_file(archivant, volumeID, attachmentID):
    f = archivant.get_file(volumeID, attachmentID)
    attachment = archivant.get_attachment(volumeID, attachmentID)
    archivant._db.increment_download_count(volumeID, attachmentID)
    return send_file(f,
                     mimetype=attachment['metadata']['mime'],
                     attachment_filename=attachment['metadata']['name'],
                     as_attachment=True)


def routes_collector(gatherer):
    """Decorator utility to collect flask routes in a dictionary.

    This function together with :func:`add_routes` provides an
    easy way to split flask routes declaration in multiple modules.

    :param gatherer: dict in which will be collected routes

    The decorator provided by this function should be used as the
    `original flask decorator <http://flask.pocoo.org/docs/latest/api/#flask.Flask.route>`_
    example::

       routes = []
       route = routes_collector(routes)

       @route('/volumes/', methods=['GET', 'POST'])
       def volumes():
           return 'page body'

    After you've collected your routes you can use :func:`add_routes` to register
    them onto the main blueprint/flask_app.
    """
    def hatFunc(rule, **options):
        def decorator(f):
            rule_dict = {'rule':rule, 'view_func':f}
            rule_dict.update(options)
            gatherer.append(rule_dict)
        return decorator
    return hatFunc


def add_routes(fapp, routes, prefix=""):
    """Batch routes registering

    Register routes to a blueprint/flask_app previously collected
    with :func:`routes_collector`.

    :param fapp: bluprint or flask_app to whom attach new routes.
    :param routes: dict of routes collected by :func:`routes_collector`
    :param prefix: url prefix under which register all routes
    """
    for r in routes:
        r['rule'] = prefix + r['rule']
        fapp.add_url_rule(**r)


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
