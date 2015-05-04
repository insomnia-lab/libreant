from fsdb import Fsdb
from libreantdb import DB
from elasticsearch import Elasticsearch

from logging import getLogger
log = getLogger('archivant')


class Archivant():
    ''' Implementation of a Data Access Layer

        Archivant handling both an fsdb instance and
        a libreantdb one exposes an API to operate on 'volumes'.

        A 'volume' represents a physical/digital object stored within archivant.
        Volumes are structured as described in `Archivant.normalize_volume`,
        these have metadata and a list of attachments.
    '''

    def __init__(self, conf={}):
        defaults = {
            'FSDB_PATH': "",
            'ES_HOSTS': None,
            'ES_INDEXNAME': ''
        }
        defaults.update(conf)
        self._config = defaults
        log.debug('initializing with this config: ' + str(self._config))

        # initialize fsdb
        if not self._config['FSDB_PATH']:
            raise ValueError('FSDB_PATH cannot be empty')
        self._fsdb = Fsdb(self._config['FSDB_PATH'])

        # initialize elasticsearch
        if not self._config['ES_INDEXNAME']:
            raise ValueError('ES_INDEXNAME cannot be empty')
        db = DB(Elasticsearch(hosts=self._config['ES_HOSTS']),
                index_name=self._config['ES_INDEXNAME'])
        db.setup_db()
        self._db = db
