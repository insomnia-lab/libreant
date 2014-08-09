def validate_book(body):
    if 'language' not in body:
        raise ValueError('language needed')
    if len(body['language']) > 2:
        raise ValueError('invalid language: %s' % body['language'])
    allfields = []
    for name, field in body.items():
        if name.startswith('_') or name == 'language':
            continue
        if type(field) in (str, unicode):
            separate = field.split()
        elif type(field) is (list):
            separate = field
        else:
            continue
        for f in separate:
            allfields.append(f)

    body['text_%s' % body['language']] = ' '.join(allfields)
    return body


class DB(object):
    '''
    this class contains every query method and every operation on the index
    '''
    # Setup {{{2
    def __init__(self, es):
        self.es = es
        self.index_name = 'book'
        # book_validator can adjust the book, and raise if it's not valid
        self.book_validator = validate_book

    def setup_db(self):
        maps = {
            'book': {  # this need to be the document type!
                "properties": {
                    "text_en": {
                        "type": "string",
                        "analyzer": "english"
                    },
                    "text_it": {
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
    def _search(self, body, size=30):
        return self.es.search(index=self.index_name, body=body, size=size)

    def _get_search_field(self, field, value):
        return {'query':
                {'match': {field: value}}
                }

    def mlt(self, _id):
        '''
        High-level method to do "more like this".

        Its exact implementation can vary; at the moment it just searches by
        title, but it could change
        '''
        # query = {'mlt': {
        #     'fields': ['book.text_it'],
        #     'ids': [_id],
        #     'min_term_freq': 1}}
        book = self.get_book_by_id(_id)
        from pprint import pprint
        pprint(book)
        ret = self.get_books_by_title(book['_source']['title'])
        # "fixing" the results, changing main fields. This sucks, because other
        # fields (ie: max_score) can be wrong now
        h = [b for b in ret['hits']['hits'] if b['_id'] != _id]
        ret['hits']['hits'] = h
        ret['hits']['total'] = ret['hits']['total'] - 1
        pprint(ret)
        return ret

    def get_all_books(self):
        return self._search({})

    def get_books_simplequery(self, query):
        return self._search(self._get_search_field('_all', query))

    def get_books_multilanguage(self, query):
        return self._search({'query': {'multi_match':
                                       {'query': query, 'fields': 'text_*'}
                                       }})

    def get_books_by_title(self, title):
        return self._search(self._get_search_field('title', title))

    def get_books_by_actor(self, authorname):
        return self._search(self._get_search_field('actors', authorname))

    def get_book_by_id(self, id):
        return self.es.get(index=self.index_name, id=id)

    def user_search(self, query):
        '''
        This acts like a "wrapper" that always point to the recommended
        function for user searching.
        '''
        return self.get_books_multilanguage(query)

    def autocomplete(self, fieldname, start):
        raise NotImplementedError()
    # End queries }}}

    # Operations {{{2
    def add_book(self, **book):
        '''
        Call it like this:
            db.add_book(doc_type='book',
                        body={'title': 'foobar'})
        '''
        if 'doc_type' not in book:
            book['doc_type'] = 'book'
        book['body'] = validate_book(book['body'])
        return self.es.create(index=self.index_name, **book)
    # End operations }}}

# vim: set fdm=marker fdl=1:
