import tempfile
import logging
import os

from flask import Flask, render_template, request, abort, Response, redirect, url_for, send_file, make_response
from werkzeug import secure_filename
from utils import requestedFormat
from flask_bootstrap import Bootstrap
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch import exceptions as es_exceptions
from flask.ext.babel import Babel, gettext, get_locale
from babel.dates import format_timedelta
from datetime import datetime

from presets import PresetManager
from constants import isoLangs
from fsdb import Fsdb

from libreantdb import DB
from agherant import agherant
from webserver_utils import gevent_run
import config_utils


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
        self._db = None
        if not self.config['FSDB_PATH']:
            if not self.config['DEBUG']:
                raise ValueError('FSDB_PATH cannot be empty')
            else:
                fsdbPath = os.path.join(tempfile.gettempdir(), 'libreant_fsdb')
                self.fsdb = Fsdb(fsdbPath)
        else:
            self.fsdb = Fsdb(self.config['FSDB_PATH'])
        self.presetManager = PresetManager(self.config['PRESET_PATHS'])

    def get_db(self):
        if self._db is None:
            db = DB(Elasticsearch(hosts=self.config['ES_HOSTS']),
                    index_name=self.config['ES_INDEXNAME'])
            db.setup_db()
            # deferring assignment is meant to avoid that we _first_ cache the
            # DB object, then the setup_db() fails. This will let us with a
            # non-setupped DB
            self._db = db
        return self._db


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
        Bootstrap(self)
        self.babel = Babel(self)


def initLoggers(logLevel=logging.WARNING):
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s [%(name)s] [%(levelname)s] %(message)s')
    streamHandler.setFormatter(formatter)
    loggers = map(logging.getLogger,
                  ('webant', 'fsdb', 'presets', 'agherant', 'config_utils'))
    for logger in loggers:
        logger.setLevel(logLevel)
        if not logger.handlers:
            logger.addHandler(streamHandler)


def create_app():
    initLoggers()
    conf = {'DEBUG': True}
    conf.update(config_utils.from_envvar_file('WEBANT_SETTINGS'))
    conf.update(config_utils.from_envvars(prefix='WEBANT_'))
    initLoggers(logging.DEBUG if conf.get('DEBUG', False) else logging.WARNING)
    app = LibreantViewApp("webant", conf)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/search')
    def search():
        query = request.args.get('q', None)
        if query is None:
            abort(400, "No query given")
        res = app.get_db().user_search(query)['hits']['hits']
        books = []
        for b in res:
            src = b['_source']
            src['_id'] = b['_id']
            src['_score'] = b['_score']
            books.append(src)
        format = requestedFormat( request,
                                  ['text/html',
                                   'text/xml',
                                   'application/rss+xml',
                                   'opensearch'])
        if format == 'text/html':
            return render_template('search.html', books=books, query=query)
        if format in ['opensearch', 'text/xml','application/rss+xml']:
            return Response(render_template('opens.xml',
                                            books=books, query=query),
                            mimetype='text/xml')

    @app.route('/add', methods=['POST'])
    def upload():
        requiredFields = ['_language']
        optFields = ['_preset']
        body= {}

        #TODO check also for preset consistency?

        for requiredField in requiredFields:
            if requiredField not in request.form:
                renderErrorPage(gettext('Required field "%(mField)s is missing',
                                mField=requiredField), 400)
            else:
                body[requiredField] = request.form[requiredField]

        for optField in optFields:
            if optField in request.form:
                body[optField] = request.form[optField]

        for key,value in request.form.items():
            if key.startswith('field_') and value:
                body[key[6:]] = value

        files = []
        for upName,upFile in request.files.items():
            tmpFile, tmpFilePath = tempfile.mkstemp()
            upFile.save(tmpFilePath)
            fileInfo = {}
            fileInfo['name'] = secure_filename(upFile.filename)
            fileInfo['size'] = os.path.getsize(tmpFilePath)
            fileInfo['mime'] = upFile.mimetype
            fileInfo['notes'] = request.form[upName+'_notes']
            fileInfo['sha1'] = Fsdb.fileDigest(tmpFilePath, algorithm="sha1")
            fileInfo['download_count'] = 0
            fsdb_id = app.fsdb.add(tmpFilePath)
            # close and delete tmpFile
            os.close(tmpFile)
            os.remove(tmpFilePath)

            fileInfo['fsdb_id'] = fsdb_id
            files.append(fileInfo)

        if len(files) > 0:
            body['_files'] = files

        addedItem = app.get_db().add_book(doc_type="book", body=body)
        return redirect(url_for('view_book',bookid=addedItem['_id']))

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

    @app.route('/view/<bookid>')
    def view_book(bookid):
        try:
             b = app.get_db().get_book_by_id(bookid)
        except NotFoundError, e:
             return renderErrorPage(message='no element found with id "{}"'.format(bookid), httpCode=404)
        similar = app.get_db().mlt(bookid)['hits']['hits'][:10]
        return render_template('details.html',
                               book=b['_source'], bookid=bookid,
                               similar=similar)

    @app.route('/download/<bookid>/<fileid>')
    def download_book(bookid, fileid):
        try:
            b = app.get_db().get_book_by_id(bookid)
        except NotFoundError, e:
            return renderErrorPage(message='no element found with id "{}"'.format(bookid), httpCode=404)
        if '_files' not in b['_source']:
            return renderErrorPage(message='element with id "{}" has no files attached'.format(bookid), httpCode=404)
        for i,file in enumerate(b['_source']['_files']):
            if file['sha1'] == fileid:
                try:
                    app.get_db().increment_download_count(bookid, i)
                except:
                    app.logger.warn("Cannot increment download count",
                                    exc_info=1)
                return send_file(app.fsdb.getFilePath(file['fsdb_id']),
                                  mimetype=file['mime'],
                                  attachment_filename=file['name'],
                                  as_attachment=True)
        # no file found with the given digest
        return renderErrorPage(message='no file found with id "{}" on item "{}"'.format(fileid, bookid), httpCode=404)

    @app.route('/recents')
    def recents():
        res = app.get_db().get_last_inserted()['hits']['hits']
        return render_template('recents.html', items=res)

    @app.babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(['en', 'it', 'sq'])

    @app.template_filter('timepassedformat')
    def timepassedformat_filter(timestamp):
        '''given a timestamp it returns a string
           repesenting the time delta from now formatted in human language
           according to the client locale
        '''
        try:
            delta = datetime.fromtimestamp(timestamp/1000) - datetime.now()
            return format_timedelta(delta, granularity='second', add_direction=True, format='medium', locale=get_locale())
        except Exception:
            app.logger.exception("could not convert timestamp")
            return timestamp

    @app.errorhandler(es_exceptions.ConnectionError)
    def handle_elasticsearch_down(error):
        rsp = make_response('DB connection error', 503)
        app.logger.error("Error connecting to DB; check your configuration")
        return rsp

    return app


def renderErrorPage(message, httpCode):
    return render_template('error.html', message=message, code=httpCode), httpCode

def main():
    app = create_app()
    gevent_run(app)

if __name__ == '__main__':
    main()
