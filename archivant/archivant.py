import os
from numbers import Integral
from elasticsearch import Elasticsearch
from elasticsearch import NotFoundError
from uuid import uuid4
from fsdb import Fsdb
from fsdb.hashtools import calc_file_digest, calc_digest
from copy import deepcopy
from urlparse import urlparse
from json import dumps

from libreantdb import DB
from exceptions import NotFoundException, FileOpNotSupported

from logging import getLogger
log = getLogger('archivant')


class Archivant():
    ''' Implementation of a Data Access Layer

        Archivant handles both an fsdb instance and
        a libreantdb one and exposes an high-level API to operate on 'volumes'.

        A 'volume' represents a physical/digital object stored within archivant.
        Volumes are structured as described in :meth:`~Archivant.normalize_volume`;
        shortly, they have language, metadata and attachments.
        An attachment is an URL plus some metadata.

        If you won't configure the FSDB_PATH parameter, fsdb will not be initialized
        and archivant will start in metadata-only mode.
        In metdata-only mode all file related functions will raise FileOpNotSupported.
    '''

    def __init__(self, conf={}):
        defaults = {
            'FSDB_PATH': None,
            'ES_HOSTS': None,
            'ES_INDEXNAME': None
        }
        defaults.update(conf)
        self._config = defaults
        log.debug('initializing with this config: ' + dumps(self._config))

        # initialize fsdb
        if self._config['FSDB_PATH']:
            self.__fsdb = Fsdb(self._config['FSDB_PATH'])
        else:
            log.warning('It has not been set any value for FSDB_PATH, file operations will not be supported')

        # initialize elasticsearch
        if not self._config['ES_INDEXNAME']:
            raise ValueError('ES_INDEXNAME cannot be empty')
        self.__db = None

    @property
    def _db(self):
        if self.__db is None:
            db = DB(Elasticsearch(hosts=self._config['ES_HOSTS']),
                    index_name=self._config['ES_INDEXNAME'])
            db.setup_db()
            self.__db = db
        return self.__db

    @property
    def _fsdb(self):
        try:
            return self.__fsdb
        except AttributeError:
            raise FileOpNotSupported("FSDB_PATH paramenter has not been set")

    def is_file_op_supported(self):
        try:
            self._fsdb
        except FileOpNotSupported:
            return False
        else:
            return True

    @staticmethod
    def normalize_volume(volume):
        '''convert volume metadata from es to archivant format

           This function makes side effect on input volume

           output example::

            {
                'id': 'AU0paPZOMZchuDv1iDv8',
                'type': 'volume',
                'metadata': {'_language': 'en',
                            'key1': 'value1',
                            'key2': 'value2',
                            'key3': 'value3'},
                'attachments': [{'id': 'a910e1kjdo2d192d1dko1p2kd1209d',
                                'type' : 'attachment',
                                'url': 'fsdb:///624bffa8a6f90813b7982d0e5b4c1475ebec40e3',
                                'metadata': {'download_count': 0,
                                            'mime': 'application/json',
                                            'name': 'tmp9fyat_',
                                            'notes': 'this file is awsome',
                                            'sha1': '624bffa8a6f90813b7982d0e5b4c1475ebec40e3',
                                            'size': 10}
                            }]
            }

        '''
        res = dict()
        res['type'] = 'volume'
        res['id'] = volume['_id']
        if '_score' in volume:
            res['score'] = volume['_score']

        source = volume['_source']
        attachments = source['_attachments']
        del(source['_attachments'])
        del(source['_text_' + source['_language']])
        res['metadata'] = source

        atts = list()
        for attachment in attachments:
            atts.append(Archivant.normalize_attachment(attachment))
        res['attachments'] = atts

        return res

    @staticmethod
    def normalize_attachment(attachment):
        ''' Convert attachment metadata from es to archivant format

            This function makes side effect on input attachment
        '''
        res = dict()
        res['type'] = 'attachment'
        res['id'] = attachment['id']
        del(attachment['id'])
        res['url'] = attachment['url']
        del(attachment['url'])
        res['metadata'] = attachment
        return res

    @staticmethod
    def denormalize_volume(volume):
        '''convert volume metadata from archivant to es format'''
        id = volume['id']
        res = dict()
        res.update(volume['metadata'])
        denorm_attachments = list()
        for a in volume['attachments']:
            denorm_attachments.append(Archivant.denormalize_attachment(a))
        res['_attachments'] = denorm_attachments
        return id, res

    @staticmethod
    def denormalize_attachment(attachment):
        '''convert attachment metadata from archivant to es format'''
        res = dict()
        ext = ['id', 'url']
        for k in ext:
            if k in attachment['metadata']:
                raise ValueError("metadata section could not contain special key '{}'".format(k))
            res[k] = attachment[k]
        res.update(attachment['metadata'])
        return res

    def _req_raw_volume(self, volumeID):
        try:
            return self._db.get_book_by_id(volumeID)
        except NotFoundError:
            raise NotFoundException("could not found volume with id: '{}'".format(volumeID))

    def get_all_volumes(self):
        '''iterate over all stored volumes'''
        for raw_volume in self._db.iterate_all():
            yield self.normalize_volume(raw_volume)

    def get_volume(self, volumeID):
        log.debug("Requested volume with id:'{}'".format(volumeID))
        return Archivant.normalize_volume(self._req_raw_volume(volumeID))

    def get_attachment(self, volumeID, attachmentID):
        log.debug("Requested attachment '{}' of the volume '{}'".format(attachmentID, volumeID))
        rawVolume = self._req_raw_volume(volumeID)
        for rawAttachment in rawVolume['_source']['_attachments']:
            if rawAttachment['id'] == attachmentID:
                return Archivant.normalize_attachment(rawAttachment)
        raise NotFoundException("could not found attachment '{}' of the volume '{}'".format(attachmentID, volumeID))

    def get_file(self, volumeID, attachmentID):
        log.debug("Requested file associated with attachment '{}' of the volume '{}'".format(attachmentID, volumeID))
        attachment = self.get_attachment(volumeID, attachmentID)
        return self._resolve_url(attachment['url'])

    def delete_attachments(self, volumeID, attachmentsID):
        ''' delete attachments from a volume '''
        log.debug("deleting attachments from volume '{}': {}".format(volumeID, attachmentsID))
        rawVolume = self._req_raw_volume(volumeID)
        insID = [a['id'] for a in rawVolume['_source']['_attachments']]
        # check that all requested file are present
        for id in attachmentsID:
            if id not in insID:
                raise NotFoundException("could not found attachment '{}' of the volume '{}'".format(id, volumeID))
        for index, id in enumerate(attachmentsID):
            rawVolume['_source']['_attachments'].pop(insID.index(id))
        self._db.modify_book(volumeID, rawVolume['_source'], version=rawVolume['_version'])

    def delete_volume(self, volumeID):
        log.debug("Deleting volume: '{}'".format(volumeID))
        try:
            self._db.delete_book(volumeID)
        except NotFoundError:
            raise NotFoundException("could not found volume with id: '{}'".format(volumeID))

    def insert_attachments(self, volumeID, attachments):
        ''' add attachments to an already existing volume '''
        log.debug("adding new attachments to volume '{}': {}".format(volumeID, attachments))
        if not attachments:
            return
        rawVolume = self._req_raw_volume(volumeID)
        attsID = list()
        for index, a in enumerate(attachments):
            try:
                rawAttachment = self._assemble_attachment(a['file'], a)
                rawVolume['_source']['_attachments'].append(rawAttachment)
                attsID.append(rawAttachment['id'])
            except:
                log.exception("Error while elaborating attachments array at index: {}".format(index))
                raise
        self._db.modify_book(volumeID, rawVolume['_source'], version=rawVolume['_version'])
        return attsID

    def insert_volume(self, metadata, attachments=[]):
        '''Insert a new volume

        Returns the ID of the added volume

        `metadata` must be a dict containg metadata of the volume::

            {
              "_language" : "it",  # language of the metadata
              "key1" : "value1",   # attribute
              "key2" : "value2",
              ...
              "keyN" : "valueN"
            }

            The only required key is `_language`


        `attachments` must be an array of dict::

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
            try:
                attData = self._assemble_attachment(a['file'], a)
                attsData.append(attData)
            except:
                log.exception("Error while elaborating attachments array at index: {}".format(index))
                raise
        volume['_attachments'] = attsData

        log.debug('constructed volume for insertion: {}'.format(volume))
        addedVolume = self._db.add_book(body=volume)
        log.debug("added new volume: '{}'".format(addedVolume['_id']))
        return addedVolume['_id']

    def _assemble_attachment(self, file, metadata):
        ''' store file and return a dict containing assembled metadata

            param `file` must be a path or a File Object
            param `metadata` must be a dict:
                {
                  "name"  : "nome_buffo.ext"         # name of the file (extension included) [optional if a path was given]
                  "mime"  : "application/json"       # mime type of the file [optional]
                  "notes" : "this file is awesome"   # notes about this file [optional]
                }
        '''
        res = dict()

        if isinstance(file, basestring) and os.path.isfile(file):
            res['name'] = metadata['name'] if 'name' in metadata else os.path.basename(file)
            res['size'] = os.path.getsize(file)
            res['sha1'] = calc_file_digest(file, algorithm="sha1")

        elif hasattr(file, 'read') and hasattr(file, 'seek'):
            if 'name' in metadata and metadata['name']:
                res['name'] = metadata['name']
            elif hasattr(file, 'name'):
                file['name'] = file.name
            else:
                raise ValueError("Could not assign a name to the file")

            old_position = file.tell()

            file.seek(0, os.SEEK_END)
            res['size'] = file.tell() - old_position
            file.seek(old_position, os.SEEK_SET)

            res['sha1'] = calc_digest(file, algorithm="sha1")
            file.seek(old_position, os.SEEK_SET)

        else:
            raise ValueError("Unsupported file value type: {}".format(type(file)))

        res['id'] = uuid4().hex
        res['mime'] = metadata['mime'] if 'mime' in metadata else None
        res['notes'] = metadata['notes'] if 'notes' in metadata else ""
        res['download_count'] = 0
        fsdb_id = self._fsdb.add(file)
        res['url'] = "fsdb:///" + fsdb_id
        return res

    def update_volume(self, volumeID, metadata):
        '''update existing volume metadata
           the given metadata will substitute the old one
        '''
        log.debug('updating volume metadata: {}'.format(volumeID))
        rawVolume = self._req_raw_volume(volumeID)
        normalized = self.normalize_volume(rawVolume)
        normalized['metadata'] = metadata
        _, newRawVolume = self.denormalize_volume(normalized)
        self._db.modify_book(volumeID, newRawVolume)

    def update_attachment(self, volumeID, attachmentID, metadata):
        '''update an existing attachment

        the given metadata dict will be merged with the old one.
        only the following fields could be updated:
        [name, mime, notes, download_count]
        '''
        log.debug('updating metadata of attachment {} from volume {}'.format(attachmentID, volumeID))
        modifiable_fields = ['name', 'mime', 'notes', 'download_count']
        for k in metadata.keys():
            if k not in modifiable_fields:
                raise ValueError('Not modifiable field given: {}'.format(k))
        if 'name' in metadata and not isinstance(metadata['name'], basestring):
            raise ValueError("'name' must be a string")
        if 'mime' in metadata and not isinstance(metadata['mime'], basestring):
            raise ValueError("'mime' must be a string")
        if 'notes' in metadata and not isinstance(metadata['notes'], basestring):
            raise ValueError("'notes' must be a string")
        if 'download_count' in metadata and not isinstance(metadata['download_count'], Integral):
            raise ValueError("'download_count' must be a number")
        rawVolume = self._req_raw_volume(volumeID)
        for attachment in rawVolume['_source']['_attachments']:
            if attachment['id'] == attachmentID:
                attachment.update(metadata)
                self._db.modify_book(volumeID, rawVolume['_source'], rawVolume['_version'])
                return
        raise NotFoundException('Could not found attachment with id {} in volume {}'.format(attachmentID, volumeID))

    def _resolve_url(self, url):
        parseResult = urlparse(url)
        if parseResult.scheme == "fsdb":
            return self._fsdb[os.path.basename(parseResult.path)]
        else:
            raise Exception("url scheme '{}' not supported".format(parseResult.scheme))

    def dangling_files(self):
        '''iterate over fsdb files no more attached to any volume'''
        for fid in self._fsdb:
            if not self._db.file_is_attached('fsdb:///' + fid):
                yield fid

    def shrink_local_fsdb(self, dangling=True, corrupted=True, dryrun=False):
        '''shrink local fsdb by removing dangling and/or corrupted files

           return number of deleted files
        '''
        log.debug('shrinking local fsdb [danglings={}, corrupted={}]'.format(dangling, corrupted))
        count = 0
        if dangling:
            for fid in self.dangling_files():
                log.info("shrinking: removing dangling  '{}'".format(fid))
                if not dryrun:
                    self._fsdb.remove(fid)
                count += 1
        if corrupted:
            for fid in self._fsdb.corrupted():
                log.info("shrinking: removing corrupted '{}'".format(fid))
                if not dryrun:
                    self._fsdb.remove(fid)
                count += 1
        return count
