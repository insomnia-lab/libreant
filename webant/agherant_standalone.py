from flask import Flask, request
from flask_bootstrap import Bootstrap
from flask.ext.babel import Babel

import agherant
from webserver_utils import gevent_run


def create_app(conf):
    app = Flask(__name__)
    app.config.update(conf)
    Bootstrap(app)
    babel = Babel(app)
    app.register_blueprint(agherant.agherant, url_prefix='/agherant')

    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(['en', 'it', 'sq'])

    return app


def main(conf={}):
    app = create_app(conf)
    gevent_run(app)

if __name__ == '__main__':
    main()
