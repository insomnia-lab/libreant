from flask import Flask, render_template, request, abort, Response
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from elasticsearch import Elasticsearch
from flask.ext.babel import Babel
from presets import PresetManager
import logging

from libreantdb import DB
from agherant import agherant

def initLoggers():
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)

    loggers = [logging.getLogger('webant')]
    for logger in loggers:
        logger.addHandler(streamHandler)

def create_app(configfile=None):
    initLoggers()
    app = Flask("webant")
    app.config.update({
        'BOOTSTRAP_SERVE_LOCAL': True,
        'DEBUG': True,
        'PRESET_PATHS': [],
        'AGHERANT_DESCRIPTIONS': [],
        'SECRET_KEY': 'really insecure, please change me!'
    })
    AppConfig(app, configfile, default_settings=False)
    app.register_blueprint(agherant, url_prefix='/agherant')
    Bootstrap(app)
    babel = Babel(app)
    presetManager = PresetManager(app.config['PRESET_PATHS'])

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

    @app.route('/description.xml')
    def description():
        return Response(render_template('opens_desc.xml'),
                        mimetype='text/xml')

    @app.route('/view/<bookid>')
    def view_book(bookid):
        b = get_db().get_book_by_id(bookid)
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


def main():
    from gevent.wsgi import WSGIServer
    import gevent.monkey
    from werkzeug.debug import DebuggedApplication
    from werkzeug.serving import run_with_reloader
    gevent.monkey.patch_socket()
    app = create_app()
    if app.config['DEBUG']:
        app = DebuggedApplication(app)

    @run_with_reloader
    def run_server():
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()

if __name__ == '__main__':
    main()
