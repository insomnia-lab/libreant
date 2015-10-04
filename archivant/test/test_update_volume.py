from archivant.test.class_template import TestArchivant

from nose.tools import eq_
from copy import deepcopy


class TestArchivantUpdateVolume(TestArchivant):

    def test_update_volume_denormalize(self):
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(2)
        attachments[0]['notes'] = 'noteacaso'
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        rawVolume = self.arc._req_raw_volume(id)
        normalized = self.arc.normalize_volume(deepcopy(rawVolume))
        denom_id, denormalized = self.arc.denormalize_volume(normalized)
        del(rawVolume['_source']['_text_' + rawVolume['_source']['_language']])
        eq_(denom_id, id)
        eq_(denormalized, rawVolume['_source'])

    def test_update_volume_add(self):
        volume_metadata = {'_language': 'en',
                           'old_1': 'old_value_1'}
        id = self.arc.insert_volume(volume_metadata)
        volume_metadata['new_1'] = 'new_value_1'
        self.arc.update_volume(id, volume_metadata)
        vol_metadata = (self.arc.get_volume(id))['metadata']
        eq_(vol_metadata['_language'], 'en')
        eq_(vol_metadata['old_1'], 'old_value_1')
        eq_(vol_metadata['new_1'], 'new_value_1')

    def test_update_volume_change(self):
        volume_metadata = {'_language': 'en',
                           'old_1': 'old_value_1',
                           'old_2': 'old_value_2'}
        id = self.arc.insert_volume(volume_metadata)
        volume_metadata['old_2'] = 'new_value_2'
        volume_metadata['_language'] = 'it'
        self.arc.update_volume(id, volume_metadata)
        vol_metadata = (self.arc.get_volume(id))['metadata']
        eq_(vol_metadata['_language'], 'it')
        eq_(vol_metadata['old_1'], 'old_value_1')
        eq_(vol_metadata['old_2'], 'new_value_2')

    def test_update_volume_delete(self):
        volume_metadata = {'_language': 'en',
                           'old_1': 'old_value_1',
                           'old_2': 'old_value_2'}
        id = self.arc.insert_volume(volume_metadata)
        del(volume_metadata['old_2'])
        self.arc.update_volume(id, volume_metadata)
        vol_metadata = (self.arc.get_volume(id))['metadata']
        eq_(vol_metadata['_language'], 'en')
        eq_(vol_metadata['old_1'], 'old_value_1')
