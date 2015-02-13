from flask import Flask, request
from flask_bootstrap import Bootstrap
from flask.ext.babel import Babel

import agherant
from webserver_utils import gevent_run
import config_utils


def create_app():
    app = Flask(__name__)
    app.config.update({
        'AGHERANT_DESCRIPTIONS': [],
        'DEBUG': True,
        'SECRET_KEY': 'really insecure, please change me!'
    })
    app.config.update(config_utils.from_envvar_file('WEBANT_SETTINGS'))
    app.config.update(config_utils.from_envvars(prefix='WEBANT_'))
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
