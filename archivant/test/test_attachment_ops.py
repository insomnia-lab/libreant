from archivant.test import TestArchivant
from archivant.exceptions import NotFoundException

from nose.tools import eq_, raises  # , ok_


class TestArchivantAttachmentOperations(TestArchivant):

    def test_insert_attachment(self):
        volume_metadata = self.generate_volume_metadata()
        volumeID = self.arc.insert_volume(volume_metadata)
        attachments = self.generate_attachments(1)
        self.arc.insert_attachments(volumeID, attachments)
        added_attachments = self.arc.get_volume(volumeID)['attachments']
        eq_(len(added_attachments), 1)

    def test_insert_attachments(self, n=4):
        volume_metadata = self.generate_volume_metadata()
        volumeID = self.arc.insert_volume(volume_metadata)
        attachments = self.generate_attachments(n)
        self.arc.insert_attachments(volumeID, attachments)
        added_attachments = self.arc.get_volume(volumeID)['attachments']
        eq_(len(added_attachments), n)

    def test_insert_attachments_burst(self, n=4):
        volume_metadata = self.generate_volume_metadata()
        volumeID = self.arc.insert_volume(volume_metadata)
        for _ in range(n):
            attachments = self.generate_attachments(1)
            self.arc.insert_attachments(volumeID, attachments)
        added_attachments = (self.arc.get_volume(volumeID))['attachments']
        eq_(len(added_attachments), n)

    def test_delete_attachment(self):
        n = 3
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(n)
        volumeID = self.arc.insert_volume(volume_metadata, attachments=attachments)
        added_attachments = (self.arc.get_volume(volumeID))['attachments']
        self.arc.delete_attachments(volumeID, [added_attachments[n-1]['id']])
        added_attachments = (self.arc.get_volume(volumeID))['attachments']
        eq_(len(added_attachments), n-1)

    def test_delete_attachments(self):
        n = 5
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(n)
        volumeID = self.arc.insert_volume(volume_metadata, attachments=attachments)
        added_attachments = (self.arc.get_volume(volumeID))['attachments']
        self.arc.delete_attachments(volumeID, [added_attachments[n-1]['id'],
                                               added_attachments[n-3]['id'],
                                               added_attachments[0]['id']])
        added_attachments = (self.arc.get_volume(volumeID))['attachments']
        eq_(len(added_attachments), n-3)

    @raises(NotFoundException)
    def test_update_attachment_not_found(self):
        volume_metadata = self.generate_volume_metadata()
        volumeID = self.arc.insert_volume(volume_metadata)
        self.arc.update_attachment(volumeID, 'unidchenonesiste', {})

    @raises(ValueError)
    def test_update_attachment_bad_field(self):
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(1)
        volumeID = self.arc.insert_volume(volume_metadata, attachments=attachments)
        added_volume = self.arc.get_volume(volumeID)
        self.arc.update_attachment(volumeID, added_volume['attachments'][0]['id'], {'12345': 'tantononlopossomodifica'})

    def test_update_attachment(self):
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(1)
        volumeID = self.arc.insert_volume(volume_metadata, attachments=attachments)
        added_volume = self.arc.get_volume(volumeID)
        self.arc.update_attachment(volumeID, added_volume['attachments'][0]['id'], {'notes': 'new_notes'})
        added_volume = self.arc.get_volume(volumeID)
        eq_(added_volume['attachments'][0]['metadata']['notes'], 'new_notes')
