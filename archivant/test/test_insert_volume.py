from archivant.test.class_template import TestArchivant
from fsdb.hashtools import calc_file_digest, calc_digest

from nose.tools import raises, ok_, eq_
import os
from StringIO import StringIO


class TestArchivantInsertVolume(TestArchivant):

    def test_insert_volume(self):
        volume_metadata = self.generate_volume_metadata()
        self.arc.insert_volume(volume_metadata)

    @raises(KeyError)
    def test_insert_volume_without_language(self):
        self.arc.insert_volume({'key0': 'value0'})

    def test_insert_volume_check_metadata(self):
        volume_metadata = self.generate_volume_metadata()
        id = self.arc.insert_volume(volume_metadata)
        added_volume = self.arc.get_volume(id)
        ok_('id' in added_volume)
        eq_(added_volume['type'], 'volume')
        eq_(len(volume_metadata), len(added_volume['metadata']))
        for k, v in volume_metadata.items():
            eq_(added_volume['metadata'][k], v)

    def test_insert_volume_no_files(self):
        volume_metadata = self.generate_volume_metadata()
        id = self.arc.insert_volume(volume_metadata)
        added_volume = self.arc.get_volume(id)
        eq_(len(added_volume['attachments']), 0)

    def test_insert_volume_one_file(self):
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(1)
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        added_attachments = (self.arc.get_volume(id))['attachments']
        eq_(len(added_attachments), 1)
        ok_('id' in added_attachments[0])
        eq_(added_attachments[0]['type'], 'attachment')

    def test_insert_volume_one_file_default_metadata(self):
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(1)
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        att_metadata = (self.arc.get_volume(id))['attachments'][0]['metadata']
        eq_(att_metadata['mime'], None)
        eq_(att_metadata['notes'], "")

    def test_insert_volume_one_file_dinamic_metadata(self):
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(1)
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        att_metadata = (self.arc.get_volume(id))['attachments'][0]['metadata']
        eq_(att_metadata['download_count'], 0)
        eq_(att_metadata['name'], os.path.basename(attachments[0]['file']))
        eq_(att_metadata['size'], os.path.getsize(attachments[0]['file']))
        eq_(att_metadata['sha1'], calc_file_digest(attachments[0]['file'],
                                                   algorithm='sha1'))

    def test_insert_volume_one_file_mime(self):
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(1)
        attachments[0]['mime'] = 'application/json'
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        att_metadata = (self.arc.get_volume(id))['attachments'][0]['metadata']
        eq_(att_metadata['mime'], attachments[0]['mime'])

    def test_insert_volume_one_file_notes(self):
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(1)
        attachments[0]['notes'] = 'this file is awsome'
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        att_metadata = (self.arc.get_volume(id))['attachments'][0]['metadata']
        eq_(att_metadata['notes'], attachments[0]['notes'])

    def test_insert_volume_one_file_name(self):
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(1)
        attachments[0]['name'] = 'I_love.json'
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        att_metadata = (self.arc.get_volume(id))['attachments'][0]['metadata']
        eq_(att_metadata['name'], attachments[0]['name'])

    def test_insert_volume_with_three_file(self, num=3):
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(num)
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        added_attachments = (self.arc.get_volume(id))['attachments']
        eq_(len(added_attachments), num)

    @raises(ValueError)
    def test_insert_volume_with_readable_no_name(self):
        s = StringIO('unascrittaperprovare')
        volume_metadata = self.generate_volume_metadata()
        attachments = [{'file': s}]
        self.arc.insert_volume(volume_metadata, attachments=attachments)

    def test_insert_volume_with_readable(self):
        s = StringIO('unascrittaperprovare')
        volume_metadata = self.generate_volume_metadata()
        attachments = [{'file': s, 'name': 'I_love.json'}]
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        added_attachments = (self.arc.get_volume(id))['attachments']
        eq_(len(added_attachments), 1)
        ok_('id' in added_attachments[0])
        eq_(added_attachments[0]['type'], 'attachment')

    def test_insert_volume_with_readable_default_metadata(self):
        volume_metadata = self.generate_volume_metadata()
        s = StringIO('unascrittaperprovare')
        volume_metadata = self.generate_volume_metadata()
        attachments = [{'file': s, 'name': 'I_love.json'}]
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        att_metadata = (self.arc.get_volume(id))['attachments'][0]['metadata']
        eq_(att_metadata['mime'], None)
        eq_(att_metadata['notes'], "")

    def test_insert_volume_with_readable_dinamic_metadata(self):
        s = StringIO('unascrittaperprovare')
        volume_metadata = self.generate_volume_metadata()
        attachments = [{'file': s, 'name': 'I_love.json'}]
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        att_metadata = (self.arc.get_volume(id))['attachments'][0]['metadata']
        eq_(att_metadata['download_count'], 0)
        eq_(att_metadata['name'], 'I_love.json')
        eq_(att_metadata['size'], s.len)
        eq_(att_metadata['sha1'], calc_digest(StringIO('unascrittaperprovare'),
                                              algorithm='sha1'))

    @raises(ValueError)
    def test_insert_volume_with_wrong_file_type(self):
        volume_metadata = self.generate_volume_metadata()
        attachments = [{'file': "macheneso"}]
        self.arc.insert_volume(volume_metadata, attachments=attachments)
