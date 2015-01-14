from flask import Flask, request
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask.ext.babel import Babel

import agherant
from webserver_utils import gevent_run


def create_app():
    app = Flask(__name__)
    app.config.update({
        'AGHERANT_DESCRIPTIONS': [],
        'DEBUG': True,
        'SECRET_KEY': 'really insecure, please change me!'
    })
    AppConfig(app, None, default_settings=False)
    Bootstrap(app)
    babel = Babel(app)
    app.register_blueprint(agherant.agherant, url_prefix='/agherant')

    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(['en', 'it', 'sq'])

    return app


def main():
    app = create_app()
    gevent_run(app)

if __name__ == '__main__':
    main()
