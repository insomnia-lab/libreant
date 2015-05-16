import os
from elasticsearch import Elasticsearch
from uuid import uuid4
from fsdb import Fsdb
from fsdb.hashtools import calc_file_digest, calc_digest
from copy import deepcopy

from libreantdb import DB

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

    def insert_volume(self, metadata, attachments=[]):
        '''Insert a new volume

           Returns the ID of the added volume

           `metadata` must be a dict containg metadata of the volume.
           The only required key is `_language`
           {
             "_language" : "it",  # language of the metadata
             "key1" : "value1",   # attribute
             "key2" : "value2",
              ...
             "keyN" : "valueN"
           }

           `attachments` must be an array of dict
           {
               "file"  : "/prova/una/path/a/caso" # path or fp
               "name"  : "nome_buffo.ext"         # name of the file (extension included) [optional if a path was given]
               "mime"  : "application/json"       # mime type of the file [optional]
               "notes" : "this file is awesome"   # notes that will be attached to this file [optional]
           }
        '''

        log.debug("adding new volume:\n\tdata: {}\n\tfiles: {}".format(metadata, attachments))

        requiredFields = ['_language']
        for requiredField in requiredFields:
            if requiredField not in metadata:
                raise KeyError("Required field '{}' is missing".format(requiredField))

        volume = deepcopy(metadata)

        attsData = []
        for index, a in enumerate(attachments):
            attData = {}
            # file is not optional
            if 'file' not in a:
                raise KeyError("`file` key not found in attachments array at index {}".format(index))

            locator = a['file']
            if isinstance(locator, basestring):
                if not os.path.isfile(locator):
                    raise ValueError("'{}' is not a regular file. attachments array at index {}".format(locator, index))
                attData['name'] = a['name'] if 'name' in a else os.path.basename(locator)
                attData['size'] = os.path.getsize(locator)
                attData['sha1'] = calc_file_digest(locator, algorithm="sha1")

            elif hasattr(locator, 'read') and hasattr(locator, 'seek'):
                if 'name' in a and a['name']:
                    attData['name'] = a['name']
                elif hasattr(locator, 'name'):
                    attData['name'] = locator.name
                else:
                    raise ValueError("Could not assign a name to the file. attachments array at index {}".format(index))

                old_position = locator.tell()

                locator.seek(0, os.SEEK_END)
                attData['size'] = locator.tell() - old_position
                locator.seek(old_position, os.SEEK_SET)

                attData['sha1'] = calc_digest(locator, algorithm="sha1")
                locator.seek(old_position, os.SEEK_SET)

            else:
                raise ValueError("unsupported file value type {} in attachments array at index {}".format(type(locator), index))

            attData['id'] = uuid4().hex
            attData['mime'] = a['mime'] if 'mime' in a else None
            attData['notes'] = a['notes'] if 'notes' in a else ""
            attData['download_count'] = 0
            fsdb_id = self._fsdb.add(locator)
            attData['url'] = "fsdb:///" + fsdb_id
            attsData.append(attData)

        volume['_attachments'] = attsData

        log.debug('constructed volume for insertion: {}'.format(volume))
        addedVolume = self._db.add_book(body=volume)
        log.debug("added new volume: '{}'".format(addedVolume['_id']))
        return addedVolume['_id']
