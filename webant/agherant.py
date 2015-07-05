from logging import getLogger
log = getLogger('agherant')
from itertools import chain

from flask import Blueprint, render_template, abort, request, Response, \
    current_app, url_for
from werkzeug.routing import BuildError
import opensearch

from util import memoize, requestedFormat

agherant = Blueprint('agherant', __name__)
Client = memoize(opensearch.Client)


@agherant.route('/search')
def search():
    query = request.args.get('q', None)
    if query is None:
        abort(400, "No query given")
    books = aggregate(current_app.config['AGHERANT_DESCRIPTIONS'], query)
    format = requestedFormat(request,
                             ['text/html',
                              'text/xml',
                              'application/rss+xml',
                              'opensearch'])
    if (not format) or (format is 'text/html'):
        return render_template('os_search.html', books=books, query=query)
    if format in ['opensearch', 'text/xml', 'application/rss+xml']:
        return Response(render_template('os_opens.xml', books=books,
                                        query=query),
                        mimetype='text/xml')
    abort(400, "Wrong format")


def aggregate(descriptions, query):
    def autoreplace(description_url):
        if description_url == 'SELF':
            try:
                return url_for('description', _external=True)
            except BuildError:
                log.info('SELF is not a valid opensearch description if '
                         'you are not running webant')
                return None
        return description_url
    descriptions = filter(lambda x: x is not None,
                          map(autoreplace, descriptions))
    clients = []
    for url in descriptions:
        log.debug("Fetching description {}".format(url))
        try:
            clients.append(Client(url))
        except:
            log.exception("Error retrieving description for '%s'" % url)
    results = map(lambda c: c.search(query), clients)
    results = list(chain(*results))
    results.sort(key=lambda r: r.score, reverse=True)
    return results

if __name__ == '__main__':
    description_list = ['http://127.0.0.1:5000/description.xml']
    results = aggregate(description_list, 'russia')

    for result in results:
        print result.title, result.score
