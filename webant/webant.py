import tempfile
import os

from flask import Flask, render_template, request, abort, Response, redirect, url_for, make_response
from werkzeug import secure_filename
from flask_bootstrap import Bootstrap
from elasticsearch import exceptions as es_exceptions
from flask.ext.babel import Babel, gettext
from babel.dates import format_timedelta
from datetime import datetime

from presets import PresetManager
from constants import isoLangs
from util import requestedFormat, send_attachment_file
from archivant import Archivant
from archivant.exceptions import NotFoundException
from agherant import agherant
from api.blueprint_api import api
from webserver_utils import gevent_run


class LibreantCoreApp(Flask):
    def __init__(self, import_name, conf={}):
        super(LibreantCoreApp, self).__init__(import_name)
        defaults = {
            'PRESET_PATHS': [],  # defaultPreset should be loaded as default?
            'FSDB_PATH': "",
            'SECRET_KEY': 'really insecure, please change me!',
            'ES_HOSTS': None,
            'ES_INDEXNAME': 'libreant'
        }
        defaults.update(conf)
        self.config.update(defaults)

        if not self.config['FSDB_PATH']:
            if not self.config['DEBUG']:
                raise ValueError('FSDB_PATH cannot be empty')
            else:
                self.config['FSDB_PATH'] = os.path.join(tempfile.gettempdir(), 'libreant_fsdb')
        self.archivant = Archivant(conf={k: self.config[k] for k in ('FSDB_PATH', 'ES_HOSTS', 'ES_INDEXNAME')})
        self.presetManager = PresetManager(self.config['PRESET_PATHS'])


class LibreantViewApp(LibreantCoreApp):
    def __init__(self, import_name, conf={}):
        defaults = {
            'BOOTSTRAP_SERVE_LOCAL': True,
            'AGHERANT_DESCRIPTIONS': [],
        }
        defaults.update(conf)
        super(LibreantViewApp, self).__init__(import_name, defaults)
        if self.config['AGHERANT_DESCRIPTIONS']:
            self.register_blueprint(agherant, url_prefix='/agherant')
        self.register_blueprint(api, url_prefix='/api/v1')
        Bootstrap(self)
        self.babel = Babel(self)
        self.available_translations = [l.language for l in self.babel.list_translations()]


def create_app(conf):
    app = LibreantViewApp("webant", conf)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/search')
    def search():
        query = request.args.get('q', None)
        if query is None:
            abort(400, "No query given")
        res = app.archivant._db.user_search(query)['hits']['hits']
        books = []
        for b in res:
            src = b['_source']
            src['_id'] = b['_id']
            src['_score'] = b['_score']
            books.append(src)
        format = requestedFormat(request,
                                 ['text/html',
                                  'text/xml',
                                  'application/rss+xml',
                                  'opensearch'])
        if format == 'text/html':
            return render_template('search.html', books=books, query=query)
        if format in ['opensearch', 'text/xml', 'application/rss+xml']:
            return Response(render_template('opens.xml',
                                            books=books, query=query),
                            mimetype='text/xml')

    @app.route('/add', methods=['POST'])
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
    def add():
        reqPreset = request.args.get('preset', None)

        if reqPreset is not None:
            if reqPreset not in app.presetManager.presets:
                return renderErrorPage(gettext("preset not found"), 400)
            else:
                preset = app.presetManager.presets[reqPreset]
        else:
            preset = None

        return render_template('add.html', preset=preset, availablePresets=app.presetManager.presets, isoLangs=isoLangs)

    @app.route('/description.xml')
    def description():
        return Response(render_template('opens_desc.xml'),
                        mimetype='text/xml')

    @app.route('/view/<volumeID>')
    def view_volume(volumeID):
        try:
            volume = app.archivant.get_volume(volumeID)
        except NotFoundException:
            return renderErrorPage(message='no volume found with id "{}"'.format(volumeID), httpCode=404)
        similar = app.archivant._db.mlt(volume['id'])['hits']['hits'][:10]
        return render_template('details.html',
                               volume=volume, similar=similar)

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
        rsp = make_response('DB connection error', 503)
        app.logger.error("Error connecting to DB; check your configuration")
        return rsp

    @app.errorhandler(404)
    def not_found(error):
        return renderErrorPage(message='Not Found', httpCode=404)

    @app.errorhandler(500)
    def internal_server_error(error):
        return renderErrorPage(message='Internal Server Error', httpCode=500)

    return app


def renderErrorPage(message, httpCode):
    return render_template('error.html', message=message, code=httpCode), httpCode


def main(conf={}):
    app = create_app(conf)
    gevent_run(app)

if __name__ == '__main__':
    main()
