import logging

from flask import Flask, request
from flask_bootstrap import Bootstrap
from flask.ext.babel import Babel

import agherant
from webant import initLoggers
from webserver_utils import gevent_run
import config_utils


def create_app():
    initLoggers()
    conf = {'DEBUG': True,
            'AGHERANT_DESCRIPTIONS': []}
    conf.update(config_utils.from_envvar_file('WEBANT_SETTINGS'))
    conf.update(config_utils.from_envvars(prefix='WEBANT_'))
    initLoggers(logging.DEBUG if conf.get('DEBUG', False) else logging.WARNING)
    app = Flask(__name__)
    app.config.update(conf)
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
