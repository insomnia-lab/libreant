import logging

from flask import Flask, request
from flask_bootstrap import Bootstrap
from flask.ext.babel import Babel

import agherant
from utils.loggers import initLoggers
from webserver_utils import gevent_run
from utils import config_utils


def create_app():
    initLoggers(logNames=['config_utils'])
    defaults = {'DEBUG': True,
                'AGHERANT_DESCRIPTIONS': []}
    conf = config_utils.load_configs('WEBANT_', defaults=defaults)
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
