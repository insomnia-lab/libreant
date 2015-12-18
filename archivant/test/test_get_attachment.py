from archivant.test.class_template import TestArchivant
from StringIO import StringIO

from nose.tools import eq_


class TestArchivantGetAttachment(TestArchivant):

    def test_get_attachment(self):
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(1)
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        added_volume = self.arc.get_volume(id)
        self.arc.get_attachment(id, added_volume['attachments'][0]['id'])

    def test_get_file(self):
        content = "unascrittaperprovare"
        volume_metadata = self.generate_volume_metadata()
        s = StringIO(content)
        volume_metadata = self.generate_volume_metadata()
        attachments = [{'file': s, 'name': 'I_love.json'}]
        volumeID = self.arc.insert_volume(volume_metadata, attachments=attachments)
        added_volume = self.arc.get_volume(volumeID)
        file = self.arc.get_file(volumeID, added_volume['attachments'][0]['id'])
        eq_(file.read(), content)
