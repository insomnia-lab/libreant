class DB(object):
    '''
    this class contains every query method and every operation on the index
    '''
    # Setup {{{2
    def __init__(self, es):
        self.es = es
        self.index_name = 'book'

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
        return self.es.create(index=self.index_name, **book)
    # End operations }}}

# vim: set fdm=marker fdl=1:
