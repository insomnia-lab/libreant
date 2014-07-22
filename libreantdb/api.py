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

    body['text_%s' % body['language']] = allfields
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
        self.es.indices.create(index=self.index_name, ignore=400)
    # End setup }}

    # Queries {{{2
    def _search(self, body):
        return self.es.search(index=self.index_name, body=body)

    def _get_search_field(self, field, value):
        return {'query':
                {'match': {field: value}}
                }

    def get_all_books(self):
        return self._search({})

    def get_books_simplequery(self, query):
        return self._search(self._get_search_field('_all', query))

    def get_books_by_title(self, title):
        return self._search(self._get_search_field('title', title))

    def get_books_by_actor(self, authorname):
        return self._search(self._get_search_field('actors', authorname))

    def get_book_by_id(self, id):
        return self.es.get(index=self.index_name, id=id)

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
        book['body'] = validate_book(book['body'])
        return self.es.create(index=self.index_name, **book)
    # End operations }}}

# vim: set fdm=marker fdl=1:
