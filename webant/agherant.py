from itertools import chain

from flask import Blueprint, render_template, abort, request, Response, jsonify
from opensearch import Client

description_list = ['http://127.0.0.1:5000/description.xml']

agherant = Blueprint('agherant', __name__)


@agherant.route('/search')
def search():
    query = request.args.get('q', None)
    if query is None:
        abort(400, "No query given")
    books = aggregate(description_list, query)
    format = request.args.get('format', 'html')
    if format == 'html':
        return render_template('os_search.html', books=books, query=query)
    if format == 'opensearch':
        return Response(render_template('os_opens.xml', books=books,
                                        query=query),
                        mimetype='text/xml')
    if format == 'json':
        return jsonify(dict(results=books))
    abort(400, "Wrong format")


def aggregate(descriptions, query):
    clients = map(Client, descriptions)
    results = map(lambda c: c.search(query), clients)
    results = list(chain(*results))
    results.sort(key=lambda r: r.score, reverse=True)
    return results

if __name__ == '__main__':
    results = aggregate(description_list, 'russia')

    for result in results:
        print result.title, result.score
