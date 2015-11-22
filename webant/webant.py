import tempfile
import os

from flask import Flask, render_template, request, Response, redirect, url_for
from werkzeug import secure_filename
from flask_bootstrap import Bootstrap
from elasticsearch import exceptions as es_exceptions
from flask.ext.babel import Babel, gettext
from babel.dates import format_timedelta
from datetime import datetime
from logging import getLogger

from presets import PresetManager
from constants import isoLangs
from util import requestedFormat, send_attachment_file
from archivant import Archivant
from archivant.exceptions import NotFoundException, FileOpNotSupported
from agherant import agherant
from api.blueprint_api import api
from webserver_utils import gevent_run
import users
import util
from authbone.authorization import CapabilityMissingException


class LibreantCoreApp(Flask):
    def __init__(self, import_name, conf={}):
        super(LibreantCoreApp, self).__init__(import_name)
        defaults = {
            'PRESET_PATHS': [],  # defaultPreset should be loaded as default?
            'FSDB_PATH': "",
            'SECRET_KEY': 'really insecure, please change me!',
            'ES_HOSTS': None,
            'ES_INDEXNAME': 'libreant',
            'USERS_DATABASE': "",
            'PWD_ROUNDS': None,
            'PWD_SALT_SIZE': None
        }
        defaults.update(conf)
        self.config.update(defaults)

        '''dirty trick: prevent default flask handler to be created
           in flask version > 0.10.1 will be a nicer way to disable default loggers
           tanks to this new code mitsuhiko/flask@84ad89ffa4390d3327b4d35983dbb4d84293b8e2
        '''
        self._logger = getLogger(self.import_name)

        self.archivant = Archivant(conf={k: self.config[k] for k in ('FSDB_PATH', 'ES_HOSTS', 'ES_INDEXNAME')})
        self.presetManager = PresetManager(self.config['PRESET_PATHS'])

        if self.config['USERS_DATABASE']:
            self.usersDB = users.init_db(self.config['USERS_DATABASE'],
                                         pwd_salt_size=self.config['PWD_SALT_SIZE'],
                                         pwd_rounds=self.config['PWD_ROUNDS'])
            users.populate_with_defaults()
        else:
            self.logger.warning("""It has not been set any value for 'USERS_DATABASE', \
all operations about users will be unsupported. Are all admins.""")
            self.usersDB = None

    @property
    def users_enabled(self):
        return bool(self.usersDB)


class LibreantViewApp(LibreantCoreApp):
    def __init__(self, import_name, conf={}):
        defaults = {
            'BOOTSTRAP_SERVE_LOCAL': True,
            'AGHERANT_DESCRIPTIONS': [],
            'API_URL': "/api/v1"
        }
        defaults.update(conf)
        super(LibreantViewApp, self).__init__(import_name, defaults)
        if self.config['AGHERANT_DESCRIPTIONS']:
            self.register_blueprint(agherant, url_prefix='/agherant')
        self.register_blueprint(api, url_prefix=self.config['API_URL'])
        Bootstrap(self)
        self.babel = Babel(self)
        self.available_translations = [l.language for l in self.babel.list_translations()]
        if self.users_enabled:
            self.autht = util.AuthtFromSession()
            self.authz = util.AuthzFromSession(authenticator=self.autht)
        else:
            self.autht = util.TransparentAutht()
            self.authz = util.TransparentAuthz()


def create_app(conf={}):
    app = LibreantViewApp("webant", conf)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/search')
    def search():
        query = request.args.get('q', None)
        if query is None:
            return renderErrorPage(message='No query given', httpCode=400)
        res = app.archivant._db.user_search(query)['hits']['hits']
        books = []
        for b in res:
            src = b['_source']
            src['_id'] = b['_id']
            src['_score'] = b['_score']
            books.append(src)
        format = requestedFormat(request,
                                 ['text/html',
                                  'text/xml', 'application/rss+xml', 'opensearch'])
        if (not format) or (format is 'text/html'):
            return render_template('search.html', books=books, query=query)
        elif format in ['opensearch', 'text/xml', 'application/rss+xml']:
            return Response(render_template('opens.xml',
                                            books=books, query=query),
                            mimetype='text/xml')
        else:
            return renderErrorPage(message='Unknown format requested', httpCode=400)

    @app.route('/add', methods=['POST'])
    @app.authz.requires_capability(('/volumes', users.Action.CREATE))
    def upload():
        requiredFields = ['_language']
        optFields = ['_preset']
        body = {}

        # TODO check also for preset consistency?

        for requiredField in requiredFields:
            if requiredField not in request.form:
                renderErrorPage(gettext("Required field '%(mField)s' is missing",
                                mField=requiredField), 400)
            else:
                body[requiredField] = request.form[requiredField]

        for optField in optFields:
            if optField in request.form:
                body[optField] = request.form[optField]

        for key, value in request.form.items():
            if key.startswith('field_') and value:
                body[key[6:]] = value

        attachments = []
        for upName, upFile in request.files.items():
            tmpFileFd, tmpFilePath = tempfile.mkstemp()
            upFile.save(tmpFilePath)
            fileInfo = {}
            fileInfo['file'] = tmpFilePath
            fileInfo['name'] = secure_filename(upFile.filename)
            fileInfo['mime'] = upFile.mimetype
            fileInfo['notes'] = request.form[upName + '_notes']
            # close fileDescriptor
            os.close(tmpFileFd)

            attachments.append(fileInfo)

        addedVolumeID = app.archivant.insert_volume(body, attachments=attachments)
        # remove temp files
        for a in attachments:
            os.remove(a['file'])
        return redirect(url_for('view_volume', volumeID=addedVolumeID))

    @app.route('/add', methods=['GET'])
    @app.authz.requires_capability(('/volumes', users.Action.CREATE))
    def add():
        reqPreset = request.args.get('preset', None)

        if reqPreset is not None:
            if reqPreset not in app.presetManager.presets:
                return renderErrorPage(gettext("preset not found"), 400)
            else:
                preset = app.presetManager.presets[reqPreset]
        else:
            preset = None
        file_upload = app.archivant.is_file_op_supported()
        return render_template('add.html', file_upload=file_upload, preset=preset, availablePresets=app.presetManager.presets, isoLangs=isoLangs)

    @app.route('/description.xml')
    def description():
        return Response(render_template('opens_desc.xml'),
                        mimetype='text/xml')

    @app.route('/view/<volumeID>')
    @app.autht.requires_authentication
    def view_volume(volumeID):
        app.authz.perform_authorization(('volumes/{}'.format(volumeID), users.Action.READ))
        try:
            volume = app.archivant.get_volume(volumeID)
        except NotFoundException:
            return renderErrorPage(message='no volume found with id "{}"'.format(volumeID), httpCode=404)
        # hide button from action toolbar if current user has not capability to perform them
        hideFromToolbar = None
        if app.users_enabled:
            currentDomain = 'volumes/{}'.format(volumeID)
            hideFromToolbar = {}
            hideFromToolbar['delete'] = not app.autht.currIdentity.can(currentDomain, users.Action.DELETE)
        similar = app.archivant._db.mlt(volume['id'])['hits']['hits'][:10]
        return render_template('details.html',
                               volume=volume,
                               similar=similar,
                               hide_from_toolbar=hideFromToolbar,
                               api_url=app.config['API_URL'])

    @app.route('/download/<volumeID>/<attachmentID>')
    def download_attachment(volumeID, attachmentID):
        try:
            return send_attachment_file(app.archivant, volumeID, attachmentID)
        except NotFoundException:
            # no attachment found with the given id
            return renderErrorPage(message='no attachment found with id "{}" on volume "{}"'.format(attachmentID, volumeID), httpCode=404)

    @app.route('/recents')
    def recents():
        res = app.archivant._db.get_last_inserted()['hits']['hits']
        return render_template('recents.html', items=res)

    @app.babel.localeselector
    def get_locale():
        if 'lang' in request.values:
            if request.values['lang'] in app.available_translations:
                return request.values['lang']
        return request.accept_languages.best_match(app.available_translations)

    if app.users_enabled:
        @app.route('/login', methods=['GET'])
        def login_form():
            if app.autht.is_logged_in():
                return renderErrorPage('you are already logged in', 400)
            return render_template('login.html')

        @app.route('/login', methods=['POST'])
        def login():
            name = request.form.get('username', None)
            pwd = request.form.get('password', None)
            if not name:
                return render_template('login.html', message='Missing username'), 400
            elif not pwd:
                return render_template('login.html', message='Missing password'), 400
            try:
                usr = users.api.get_user(name=name)
            except users.api.NotFoundException:
                return render_template('login.html', message='"{}" is not registered'.format(name)), 400
            if usr.verify_password(pwd):
                app.autht.login(usr.id)
                return redirect(url_for('index'), code=302)
            return render_template('login.html', message='Wrong password')

        @app.route('/logout')
        def logout():
            if not app.autht.is_logged_in():
                return renderErrorPage('you are not logged in', 400)
            app.autht.logout()
            return redirect(url_for('index'), code=302)

        def current_user():
            app.autht.perform_authentication()
            if users.api.is_anonymous(app.autht.currIdentity):
                return None
            return app.autht.currIdentity

        @app.context_processor
        def user_processor():
            return dict(users_enabled = True, current_user = current_user)

    @app.template_filter('timepassedformat')
    def timepassedformat_filter(timestamp):
        '''given a timestamp it returns a string
           repesenting the time delta from now formatted in human language
           according to the client locale
        '''
        try:
            delta = datetime.fromtimestamp(timestamp / 1000) - datetime.now()
            return format_timedelta(delta, granularity='second', add_direction=True, format='medium', locale=get_locale())
        except Exception:
            app.logger.exception("could not convert timestamp")
            return timestamp

    @app.errorhandler(es_exceptions.ConnectionError)
    def handle_elasticsearch_down(error):
        app.logger.exception("Error connecting to DB; check your configuration")
        return renderErrorPage(message='DB connection error', httpCode=503)

    @app.errorhandler(404)
    def not_found(error):
        return renderErrorPage(message='Not Found', httpCode=404)

    @app.errorhandler(FileOpNotSupported)
    @app.errorhandler(500)
    def internal_server_error(error):
        return renderErrorPage(message='Internal Server Error', httpCode=500)

    @app.errorhandler(CapabilityMissingException)
    def not_authenticated_handler(error):
        return renderErrorPage(message='Authorization Required', httpCode=401)

    return app


def renderErrorPage(message, httpCode):
    return render_template('error.html', message=message, code=httpCode), httpCode


def main(conf={}):
    app = create_app(conf)
    gevent_run(app)

if __name__ == '__main__':
    main()
