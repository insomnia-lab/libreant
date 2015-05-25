from archivant.test import TestArchivant
from fsdb.hashtools import calc_file_digest, calc_digest

from nose.tools import raises, ok_, eq_
import os
from copy import deepcopy
from StringIO import StringIO


class TestArchivantUpdateVolume(TestArchivant):

    def test_update_volume_denormalize(self):
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(2)
        attachments[0]['notes'] = 'noteacaso'
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        rawVolume = self.arc._req_raw_volume(id)
        normalized = self.arc.normalize_volume(deepcopy(rawVolume))
        denom_id, denormalized = self.arc.denormalize_volume(normalized)
        del(rawVolume['_source']['_text_'+rawVolume['_source']['_language']])
        eq_(denom_id, id)
        eq_(denormalized, rawVolume['_source'])
