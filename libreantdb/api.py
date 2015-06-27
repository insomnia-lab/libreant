from elasticsearch import NotFoundError
from elasticsearch.helpers import scan

import logging
log = logging.getLogger(__name__)


def validate_book(body):
    '''
    This does not only accept/refuse a book. It also returns an ENHANCED
    version of body, with (mostly fts-related) additional fields.

    This function is idempotent.
    '''
    if '_language' not in body:
        raise ValueError('language needed')
    if len(body['_language']) > 2:
        raise ValueError('invalid language: %s' % body['_language'])

    # remove old _text_* fields
    for k in body.keys():
        if k.startswith('_text'):
            del(body[k])

    allfields = collectStrings(body)
    body['_text_%s' % body['_language']] = ' '.join(allfields)
    return body


def collectStrings(leftovers):
    strings = []
    if isinstance(leftovers, basestring):
        return leftovers.split()
    elif isinstance(leftovers, list):
        for l in leftovers:
            strings.extend(collectStrings(l))
        return strings
    elif isinstance(leftovers, dict):
        for key, value in leftovers.items():
            if not key.startswith('_'):
                strings.extend(collectStrings(value))
        return strings
    else:
        return strings


class DB(object):
    '''
    This class contains every query method and every operation on the index

    The following elasticsearch body response example provides the typical structure of a single document.

    .. code-block:: ruby

        {
          "_index" : "libreant",
          "_type" : "book",
          "_id" : "AU4RleAfD1zQdqx6OQ8Y",
          "_version" : 1,
          "found" : true,
          "_source": {"_language": "en",
                      "_text_en": "marco belletti pdf file latex manual",
                      "author": "marco belletti",
                      "type": "pdf file",
                      "title": "latex manual",
                      "_attachments": [{"sha1": "dc8dc34b3e0fec2377e5cf9ea7e4780d87ff18c5",
                                        "name": "LaTeX_Wikibook.pdf",
                                        "url": "fsdb:///dc8dc34b3e0fec2377e5cf9ea7e4780d87ff18c5",
                                        "notes": "A n example bookLatex wikibook",
                                        "mime": "application/pdf",
                                        "download_count": 7,
                                        "id": "17fd3d898a834e2689340cc8aacdebb4",
                                        "size": 23909451}]
                     }
        }
    '''
    # Setup {{{2
    def __init__(self, es, index_name):
        self.es = es
        self.index_name = index_name
        # book_validator can adjust the book, and raise if it's not valid
        self.book_validator = validate_book

    def setup_db(self, wait_for_ready=True):
        ''' Create and configure index

            If `wait_for_ready` is True, this function will block until
            status for `self.index_name` will be `yellow`
        '''
        maps = {
            'book': {  # this need to be the document type!
                # special elasticsearch field
                # http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/mapping-timestamp-field.html
                # initialized with element creation date, hidden by default in query result
                "_timestamp": {"enabled": "true",
                               "store": "yes"},
                "properties": {
                    "_text_en": {
                        "type": "string",
                        "analyzer": "english"},
                    "_text_it": {
                        "type": "string",
                        "analyzer": "it_analyzer"}
                }
            }
        }

        # Just like the default one
        # http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/analysis-lang-analyzer.html#italian-analyzer
        # but the stemmer changed from light_italian to italian
        settings = {"analysis": {
            "filter": {
                "italian_elision": {
                    "type": "elision",
                    "articles": [
                        "c", "l", "all", "dall", "dell",
                        "nell", "sull", "coll", "pell",
                        "gl", "agl", "dagl", "degl", "negl",
                        "sugl", "un", "m", "t", "s", "v", "d"
                    ]
                },
                "italian_stop": {
                    "type": "stop", "stopwords": "_italian_"},
                "italian_stemmer": {
                    "type": "stemmer", "language": "italian"}
            },
            "analyzer": {
                "it_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "italian_elision",
                        "lowercase",
                        "italian_stop",
                        "italian_stemmer"
                    ]
                }
            }
        }}

        if not self.es.indices.exists(self.index_name):
            self.es.indices.create(index=self.index_name,
                                   body={'settings': settings,
                                         'mappings': maps})
        if wait_for_ready:
            log.debug('waiting for index "{}" to be ready'.format(self.index_name))
            self.es.cluster.health(index=self.index_name, level='index', wait_for_status='yellow')
            log.debug('index "{}" is now ready'.format(self.index_name))
    # End setup }}

    # Queries {{{2
    def __len__(self):
        return self.es.count(index=self.index_name)['count']

    def _search(self, body, **kargs):
        return self.es.search(index=self.index_name, body=body, **kargs)

    def _get_search_field(self, field, value):
        return {'query':
                {'match': {field: value}}
                }

    def mlt(self, _id):
        '''
        High-level method to do "more like this".

        Its exact implementation can vary.
        '''
        query = {'more_like_this': {
            # FIXME: text_* does not seem to work, so we're relying on listing
            # them manually
            'fields': ['book._text_it', 'book._text_en'],
            'ids': [_id],
            'min_term_freq': 1,
            'min_doc_freq': 1,
        }}
        return self._search(dict(query=query))

    def get_all_books(self, size=30):
        return self._search({}, size=size)

    def iterate_all(self):
        return scan(self.es, index=self.index_name)

    def get_last_inserted(self, size=30):
        query = {"fields": ["_timestamp", "_source"],
                 "query": {"match_all": {}},
                 "sort": [{"_timestamp": "desc"}]}
        return self._search(body=query, size=size)

    def get_books_simplequery(self, query):
        return self._search(self._get_search_field('_all', query))

    def get_books_multilanguage(self, query):
        return self._search({'query': {'multi_match':
                                       {'query': query, 'fields': '_text_*'}
                                       }})

    def get_books_by_title(self, title):
        return self._search(self._get_search_field('title', title))

    def get_books_by_actor(self, authorname):
        return self._search(self._get_search_field('actors', authorname))

    def get_book_by_id(self, id):
        return self.es.get(index=self.index_name, id=id)

    def get_books_querystring(self, query, **kargs):
        q = {'query': query, 'fields': ['_text_*']}
        return self._search({'query': dict(query_string=q)}, **kargs)

    def user_search(self, query):
        '''
        This acts like a "wrapper" that always point to the recommended
        function for user searching.
        '''
        return self.get_books_querystring(query)

    def file_is_attached(self, url):
        '''return true if at least one book has
           file with the given url as attachment
        '''
        body = self._get_search_field('_attachments.url', url)
        return self.es.count(index=self.index_name, body=body)['count'] > 0

    def autocomplete(self, fieldname, start):
        raise NotImplementedError()
    # End queries }}}

    # Operations {{{2
    def add_book(self, **book):
        '''
        Call it like this:
            db.add_book(doc_type='book',
            body={'title': 'foobar', '_language': 'it'})
        '''
        if 'doc_type' not in book:
            book['doc_type'] = 'book'
        book['body'] = validate_book(book['body'])
        return self.es.create(index=self.index_name, **book)

    def delete_book(self, id):
        self.es.delete(index=self.index_name,
                       id=id,
                       doc_type='book')

    def update_book(self, id, body, doc_type='book'):
        ''' Update a book

            The "body" is merged with the current one.
            Yes, it is NOT overwritten.

            In case of concurrency conflict
            this function could raise `elasticsearch.ConflictError`
        '''
        # note that we are NOT overwriting all the _source, just merging
        book = self.get_book_by_id(id)
        book['_source'].update(body)
        validated = validate_book(book['_source'])
        ret = self.es.index(index=self.index_name, id=id,
                            doc_type=doc_type, body=validated, version=book['_version'])
        return ret

    def modify_book(self, id, body, doc_type='book', version=None):
        ''' replace the entire book body

            Instead of `update_book` this function
            will overwrite the book content with param body

            If param `version` is given, it will be checked that the
            changes are applied upon that document version.
            If the document version provided is different from the one actually found,
            an `elasticsearch.ConflictError` will be raised
        '''
        validatedBody = validate_book(body)
        params = dict(index=self.index_name, id=id, doc_type=doc_type, body=validatedBody)
        if version:
            params['version'] = version
        ret = self.es.index(**params)
        return ret

    def increment_download_count(self, id, attachmentID, doc_type='book'):
        '''
        Increment the download counter of a specific file
        '''
        body = self.es.get(index=self.index_name, id=id, doc_type='book', _source_include='_attachments')['_source']

        for attachment in body['_attachments']:
            if attachment['id'] == attachmentID:
                attachment['download_count'] += 1
                self.es.update(index=self.index_name,
                               id=id,
                               doc_type=doc_type,
                               body={"doc": {'_attachments': body['_attachments']}})
                return
        raise NotFoundError("No attachment could be found with id: {}".format(attachmentID))

    # End operations }}}

# vim: set fdm=marker fdl=1:
