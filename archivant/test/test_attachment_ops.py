from archivant.test import TestArchivant

from nose.tools import eq_  # , raises, ok_


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
