from flask import Flask, render_template, request, abort, Response, redirect, url_for, send_file
from werkzeug import secure_filename
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from elasticsearch import Elasticsearch, NotFoundError
from flask.ext.babel import Babel, gettext
from presets import PresetManager
from constants import isoLangs
from fsdb import Fsdb

import tempfile
import logging
import os

from libreantdb import DB
from agherant import agherant
from webserver_utils import gevent_run


def initLoggers():
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)

    loggers = [logging.getLogger('webant'),logging.getLogger('fsdb')]
    for logger in loggers:
        logger.addHandler(streamHandler)


def create_app(configfile=None):
    initLoggers()
    app = Flask("webant")
    app.config.update({
        'BOOTSTRAP_SERVE_LOCAL': True,
        'DEBUG': True,
        'PRESET_PATHS': [], #TODO defaultPreset should be loaded as default?
        'AGHERANT_DESCRIPTIONS': [],
        'SECRET_KEY': 'really insecure, please change me!'
    })
    AppConfig(app, configfile, default_settings=False)

    if app.config['AGHERANT_DESCRIPTIONS']:
        app.register_blueprint(agherant, url_prefix='/agherant')
    Bootstrap(app)
    babel = Babel(app)

    presetManager = PresetManager(app.config['PRESET_PATHS'])

    #TODO change fsdb path
    fsdb = Fsdb("/tmp/fsdbRoot")

    app._db = None

    def get_db():
        if app._db is None:
            db = DB(Elasticsearch())
            db.setup_db()
            # deferring assignment is meant to avoid that we _first_ cache the
            # DB object, then the setup_db() fails. This will let us with a
            # non-setupped DB
            app._db = db
        return app._db

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/search')
    def search():
        query = request.args.get('q', None)
        if query is None:
            abort(400, "No query given")
        res = get_db().user_search(query)['hits']['hits']
        books = []
        for b in res:
            src = b['_source']
            src['_id'] = b['_id']
            src['_score'] = b['_score']
            books.append(src)
        format = reuqestedFormat(['text/html','application/opensearchdescription+xml','opensearch'])
        if format == 'text/html':
            return render_template('search.html', books=books, query=query)
        if format == 'application/opensearchdescription+xml' or\
           format == 'opensearch':
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
            digest = fsdb.add(tmpFilePath)
            # close and delete tmpFile
            os.close(tmpFile)
            os.remove(tmpFilePath)

            fileInfo['digest'] = digest
            files.append(fileInfo)

        if len(files) > 0:
            body['_files'] = files

        addedItem = get_db().add_book(doc_type="book", body=body)
        return redirect(url_for('view_book',bookid=addedItem['_id']))

    @app.route('/add', methods=['GET'])
    def add():
        reqPreset = request.args.get('preset', None)

        if reqPreset is not None:
            if reqPreset not in presetManager.presets:
                return renderErrorPage(gettext("preset not found"), 400)
            else:
                preset = presetManager.presets[reqPreset]
        else:
            preset = None

        return render_template('add.html', preset=preset, availablePresets=presetManager.presets, isoLangs=isoLangs)

    @app.route('/description.xml')
    def description():
        return Response(render_template('opens_desc.xml'),
                        mimetype='text/xml')

    @app.route('/view/<bookid>')
    def view_book(bookid):
        try:        
             b = get_db().get_book_by_id(bookid)
        except NotFoundError, e:
             return renderErrorPage(message='no element found with id "{}"'.format(bookid), httpCode=404)
        similar = get_db().mlt(bookid)['hits']['hits'][:10]
        return render_template('details.html',
                               book=b['_source'], bookid=bookid,
                               similar=similar)

    @app.route('/download/<bookid>/<fname>')
    def download_book(bookid, fname):
        raise NotImplementedError()

    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(['en', 'it', 'sq'])

    def reuqestedFormat(acceptedFormat):
        """Return the response format requested by client

        Client could specify requested format using:
        (options are processed in this order)
            - `format` field in http request
            - `Accept` header in http request
        Example:
            chooseFormat(['text/html','application/json'])
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

    return app


def renderErrorPage(message, httpCode):
    return render_template('error.html', message=message, code=httpCode), httpCode

def main():
    app = create_app()
    gevent_run(app)

if __name__ == '__main__':
    main()
