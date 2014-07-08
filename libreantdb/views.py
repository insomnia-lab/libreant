from couchdb.design import ViewDefinition

from . import get_db
from _helpers import CouchView


class AllAuthors(CouchView):
    '''
    Return authors and number of books

    Example: { key: 'dante alighieri', value: 25 }
    where 25 is the number of book of him that we have
    '''
    defaults = {'group': True}

    @staticmethod
    def map(doc):
        if 'authors' in doc:
            for aut in doc['authors']:
                yield (aut, 1)

    @staticmethod
    def reduce(k, v, rereduce):
        return sum(v)


class AllBooks(CouchView):
    '''Just everything. You are probably crazy if you want it'''
    @staticmethod
    def map(doc):
        yield (doc, 1)


class KeywordBooks(CouchView):
    '''
    Return a view suitable for a poor-man FTS

    Each element is {key: "word", value: "doc_id"}
    You should NOT run it without filtering. Use it like
    KeywordBooks()(db, key='foobar')
    to get any book that talks about foobar
    '''
    defaults = {'group': True}

    @staticmethod
    def map(doc):
        for field, value in doc.items():
            if field == '_id':
                continue
            if hasattr(value, 'split'):
                seq = value.split()
            elif hasattr(value, '__iter__'):
                seq = value
            else:
                yield(value, doc['_id'])
                continue
            for word in seq:
                yield (word, doc['_id'])

    @staticmethod
    def reduce(k, v, rereduce):
        return v


def set_all_views():
    if get_db() is None:
        raise ValueError('need a real db, not None')
    couch_views = (AllAuthors(), AllBooks(), KeywordBooks())
    ViewDefinition.sync_many(get_db(), couch_views)
