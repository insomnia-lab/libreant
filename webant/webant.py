from flask import Flask, render_template, request, abort, Response, redirect, url_for, send_file
from werkzeug import secure_filename
from utils import requestedFormat
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
        'FSDB_PATH': "",
        'AGHERANT_DESCRIPTIONS': [],
        'SECRET_KEY': 'really insecure, please change me!'
    })
    AppConfig(app, configfile, default_settings=False)

    if app.config['AGHERANT_DESCRIPTIONS']:
        app.register_blueprint(agherant, url_prefix='/agherant')
    Bootstrap(app)
    babel = Babel(app)

    presetManager = PresetManager(app.config['PRESET_PATHS'])

    if not app.config['FSDB_PATH']:
        if not app.config['DEBUG']:
            raise ValueError('FSDB_PATH cannot be empty')
        else:
            fsdbPath = os.path.join(tempfile.gettempdir(),'libreant_fsdb')
            fsdb = Fsdb(fsdbPath)
    else:
        fsdb = Fsdb(app.config['FSDB_PATH'])

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
            fsdb_id = fsdb.add(tmpFilePath)
            # close and delete tmpFile
            os.close(tmpFile)
            os.remove(tmpFilePath)

            fileInfo['fsdb_id'] = fsdb_id
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

    @app.route('/download/<bookid>/<fileid>')
    def download_book(bookid, fileid):
        try:        
            b = get_db().get_book_by_id(bookid)
        except NotFoundError, e:
            return renderErrorPage(message='no element found with id "{}"'.format(bookid), httpCode=404)
        if '_files' not in b['_source']:
            return renderErrorPage(message='element with id "{}" has no files attached'.format(bookid), httpCode=404)
        for i,file in enumerate(b['_source']['_files']):
            if file['sha1'] == fileid:
                get_db().increment_download_count(bookid,i)
                return send_file(fsdb.getFilePath(file['fsdb_id']),
                                  mimetype=file['mime'],
                                  attachment_filename=file['name'],
                                  as_attachment=True)
        # no file found with the given digest
        return renderErrorPage(message='no file found with id "{}" on item "{}"'.format(fileid, bookid), httpCode=404)

    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(['en', 'it', 'sq'])

    return app


def renderErrorPage(message, httpCode):
    return render_template('error.html', message=message, code=httpCode), httpCode

def main():
    app = create_app()
    gevent_run(app)

if __name__ == '__main__':
    main()
