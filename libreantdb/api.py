from __future__ import print_function


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
    this class contains every query method and every operation on the index
    '''
    # Setup {{{2
    def __init__(self, es, index_name):
        self.es = es
        self.index_name = index_name
        # book_validator can adjust the book, and raise if it's not valid
        self.book_validator = validate_book

    def setup_db(self):
        maps = {
            'book': {  # this need to be the document type!
                # special elasticsearch field
                # http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/mapping-timestamp-field.html
                # initialized with element creation date, hidden by default in query result
                "_timestamp" : { "enabled" : "true",
                                 "store": "yes"},
                "properties": {
                    "_text_en": {
                        "type": "string",
                        "analyzer": "english"
                    },
                    "_text_it": {
                        "type": "string",
                        "analyzer": "it_analyzer"
                    }
                }
            }
        }

        # Just like the default one
        # http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/analysis-lang-analyzer.html#italian-analyzer
        # but the stemmer changed from light_italian to italian
        settings = {"analysis": {
            "filter": {
                "italian_elision": {
                    "type":         "elision",
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
                    "tokenizer":  "standard",
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
    # End setup }}

    # Queries {{{2
    def __len__(self):
        stats = self.es.indices.stats()
        return stats['indices'][self.index_name]['total']['docs']['count']

    def _search(self, body, size=30):
        return self.es.search(index=self.index_name, body=body, size=size)

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

    def get_last_inserted(self, size=30):
        query = { "fields": [ "_timestamp", "_source"],
                  "query" : { "match_all" : {} },
                  "sort" : [ {"_timestamp": "desc"} ] }
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

    def get_books_querystring(self, query):
        q = {'query': query, 'fields': ['_text_*']}
        return self._search({'query': dict(query_string=q)})

    def user_search(self, query):
        '''
        This acts like a "wrapper" that always point to the recommended
        function for user searching.
        '''
        return self.get_books_querystring(query)

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

    def update_book(self, id, doc_type='book', body={}):
        '''
        Update a book. The "body" is merged with the current one.
        Yes, it is NOT overwritten.
        '''
        # note that we are NOT overwriting all the _source, just merging
        doc = {'doc': body}
        ret = self.es.update(index=self.index_name, id=id,
                             doc_type=doc_type, body=doc)
        # text_* fields need to be "updated"; atomicity is provided by the
        # idempotency of validate_book
        book = self.get_book_by_id(ret['_id'])['_source']
        book = validate_book(book)
        ret = self.es.update(index=self.index_name, id=id,
                             doc_type=doc_type, body={'doc': book})
        return ret

    def increment_download_count(self, id, fileIndex, doc_type='book'):
        '''
        Increment the download counter of a specific file
        '''
        body = self.es.get(index=self.index_name, id=id, doc_type='book', _source_include='_files')['_source']

        body['_files'][fileIndex]['download_count'] += 1

        self.es.update(index=self.index_name, id=id,
                             doc_type=doc_type, body={"doc":body})
    # End operations }}}

# vim: set fdm=marker fdl=1:
