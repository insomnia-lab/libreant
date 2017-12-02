import time
import re

from elasticsearch import NotFoundError, RequestError, TransportError
from elasticsearch import __version__ as es_version
from elasticsearch.helpers import scan, bulk, reindex

from exceptions import MappingsException

import logging
log = logging.getLogger(__name__)

# https://www.elastic.co/guide/en/elasticsearch/reference/5.5/string.html
TEXT = 'text' if es_version[0] >= 5 else 'string'

FALSE = 'false' if es_version[0] >= 5 else 'no'


def current_time_millisec():
    return int(round(time.time() * 10**3))


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

    properties = {
        "_insertion_date": {
            "type": "long",
            "null_value": 0},
        "_language": {
            "type": TEXT,
            "index": FALSE},
        "_text_en": {
            "type": TEXT,
            "analyzer": "english"},
        "_text_it": {
            "type": TEXT,
            "analyzer": "it_analyzer"},
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

        if self.es.indices.exists(self.index_name):
            try:
                self.update_mappings()
            except MappingsException as ex:
                log.error(ex)
                log.warn('An old or wrong properties mapping has been found for index: "{0}",\
                          this could led to some errors. It is recomanded to run "libreant-db upgrade"'.format(self.index_name))
        else:
            log.debug("Index is missing: '{0}'".format(self.index_name))
            self.create_index()

        if wait_for_ready:
            log.debug('waiting for index "{}" to be ready'.format(self.index_name))
            self.es.cluster.health(index=self.index_name, level='index', wait_for_status='yellow')
            log.debug('index "{}" is now ready'.format(self.index_name))

    def update_mappings(self):
        log.debug('updating index properties mappings')
        errors = {}
        for prop_k, prop_m in self.properties.iteritems():
            try:
                self.es.indices.put_mapping(index=self.index_name, doc_type='book', body={'properties': { prop_k: prop_m}})
            except RequestError as re:
                cause = re.info['error']
                if type(cause) is dict:
                    cause = cause['root_cause'][0]['reason']
                errors[prop_k] = cause.replace('\n', ' ')

        if len(errors) > 0:
            raise MappingsException("Couldn't update index properties mapping: {0}".format(errors))

    def create_index(self, indexname=None, index_conf=None):
        ''' Create the index

            Create the index with given configuration.
            If `indexname` is provided it will be used as the new index name
            instead of the class one (:py:attr:`DB.index_name`)

            :param index_conf: configuration to be used in index creation. If this
                              is not specified the default index configuration will be used.
            :raises Exception: if the index already exists.
        '''
        if indexname is None:
            indexname = self.index_name
        log.debug("Creating new index: '{0}'".format(indexname))
        if index_conf is None:
            index_conf = {'settings': self.settings,
                          'mappings': {'book': {'properties': self.properties}}}
        try:
            self.es.indices.create(index=indexname, body=index_conf)
        except TransportError as te:
            if te.error.startswith("IndexAlreadyExistsException"):
                raise Exception("Cannot create index '{}', already exists".format(indexname))
            else:
                raise

    def clone_index(self, new_indexname, index_conf=None):
        '''Clone current index

           All entries of the current index will be copied into the newly
           created one named `new_indexname`

           :param index_conf: Configuration to be used in the new index creation.
                              This param will be passed directly to :py:func:`DB.create_index`
        '''
        log.debug("Cloning index '{}' into '{}'".format(self.index_name, new_indexname))
        self.create_index(indexname=new_indexname, index_conf=index_conf)
        reindex(self.es, self.index_name, new_indexname)

    def reindex(self, new_index=None, index_conf=None):
        '''Rebuilt the current index

           This function could be useful in the case you want to change some index settings/mappings
           and you don't want to loose all the entries belonging to that index.

           This function is built in such a way that you can continue to use the old index name,
           this is achieved using index aliases.

           The old index will be cloned into a new one with the given `index_conf`.
           If we are working on an alias, it is redirected to the new index.
           Otherwise a brand new alias with the old index name is created in such a way that
           points to the newly create index.

           Keep in mind that even if you can continue to use the same index name,
           the old index will be deleted.

           :param index_conf: Configuration to be used in the new index creation.
                              This param will be passed directly to :py:func:`DB.create_index`
        '''

        alias = self.index_name if self.es.indices.exists_alias(name=self.index_name) else None
        if alias:
            original_index=self.es.indices.get_alias(self.index_name).popitem()[0]
        else:
            original_index=self.index_name

        if new_index is None:
            mtc = re.match(r"^.*_v(\d)*$", original_index)
            if mtc:
                new_index = original_index[:mtc.start(1)] + str(int(mtc.group(1)) + 1)
            else:
                new_index = original_index + '_v1'

        log.debug("Reindexing {{ alias: '{}', original_index: '{}', new_index: '{}'}}".format(alias, original_index, new_index))
        self.clone_index(new_index, index_conf=index_conf)

        if alias:
            log.debug("Moving alias from ['{0}' -> '{1}'] to ['{0}' -> '{2}']".format(alias, original_index, new_index))
            self.es.indices.update_aliases(body={
                "actions" : [
                    { "remove" : { "alias": alias, "index" : original_index} },
                    { "add" : { "alias": alias, "index" : new_index } }
                ]})

        log.debug("Deleting old index: '{}'".format(original_index))
        self.es.indices.delete(original_index)

        if not alias:
            log.debug("Crating new alias: ['{0}' -> '{1}']".format(original_index, new_index))
            self.es.indices.update_aliases(body={
                "actions" : [
                    { "add" : { "alias": original_index, "index" : new_index } }
                ]})

    # End setup }}

    # Queries {{{2
    def __len__(self):
        return self.es.count(index=self.index_name)['count']

    def _search(self, body, **kargs):
        return self.es.search(index=self.index_name,
                              body=body,
                              doc_type='book',
                              **kargs)

    def _get_search_field(self, field, value):
        return {'query':
                {'match': {field: value}}
                }

    def mlt(self, _id):
        '''
        High-level method to do "more like this".

        Its exact implementation can vary.
        '''
        query = {
            'query': {'more_like_this': {
                      'like': {'_id': _id},
                      'min_term_freq': 1,
                      'min_doc_freq': 1,
             }}
        }
        if es_version[0] <= 1:
            mlt = query['query']['more_like_this']
            mlt['ids'] = [_id]
            del mlt['like']
        return self._search(query)

    def get_all_books(self, size=30):
        return self._search({}, size=size)

    def iterate_all(self):
        return scan(self.es, index=self.index_name)

    def get_last_inserted(self, size=30):
        query = {"query": {"match_all": {}},
                 "sort": [{"_insertion_date": {"order":"desc",
                                                "missing": "_last"}}]}
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
        return self.es.get(index=self.index_name, id=id, doc_type='book')

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
    def add_book(self, body, doc_type='book'):
        '''
        Call it like this:
            db.add_book(doc_type='book',
            body={'title': 'foobar', '_language': 'it'})
        '''
        body = validate_book(body)
        body['_insertion_date'] = current_time_millisec()
        return self.es.index(index=self.index_name, doc_type=doc_type, body=body)

    def delete_book(self, id):
        self.es.delete(index=self.index_name,
                       id=id,
                       doc_type='book')

    def delete_all(self):
        '''Delete all books from the index'''
        def delete_action_gen():
            scanner = scan(self.es,
                           index=self.index_name,
                           query={'query': {'match_all':{}}})
            for v in scanner:
                yield { '_op_type': 'delete',
                        '_index': self.index_name,
                        '_type': v['_type'],
                        '_id': v['_id'],
                      }
        bulk(self.es, delete_action_gen())

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
