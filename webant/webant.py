from flask import Flask, render_template, request, abort
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from elasticsearch import Elasticsearch

from libreantdb import DB


def create_app(configfile=None):
    app = Flask(__name__)
    AppConfig(app, configfile)
    Bootstrap(app)
    if 'SECRET_KEY' not in app.config:
        # TODO remove me
        app.config['SECRET_KEY'] = 'asjdkasjdlkasdjlksajsdlsajdlsajd'

    app.db = DB(Elasticsearch())

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/search')
    def search():
        query = request.args.get('q', None)
        if query is None:
            abort(400, "No query given")
        res = app.db.get_books_simplequery(query)['hits']['hits']
        books = []
        for b in res:
            src = b['_source']
            src['_id'] = b['_id']
            books.append(src)
        print books
        return render_template('search.html', books=books)

    @app.route('/view/<bookid>')
    def view_book(bookid):
        b = app.db.get_by_id(bookid)
        return render_template('details.html', book=b)


    return app

if __name__ == '__main__':
    create_app().run(debug=True)
