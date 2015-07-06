from archivant.test.class_template import TestArchivant
from archivant.exceptions import NotFoundException

from nose.tools import raises  # , ok_, eq_


class TestArchivantDeleteVolume(TestArchivant):

    @raises(NotFoundException)
    def test_delete_wrong_volume(self):
        self.arc.delete_volume("unidchenonesiste")
        volume_metadata = self.generate_volume_metadata()
        self.arc.insert_volume(volume_metadata)

    def test_delete_volume(self):
        volume_metadata = self.generate_volume_metadata()
        volumeID = self.arc.insert_volume(volume_metadata)
        self.arc.delete_volume(volumeID)

    @raises(NotFoundException)
    def test_no_volume_aftert_deletion(self):
        volume_metadata = self.generate_volume_metadata()
        volumeID = self.arc.insert_volume(volume_metadata)
        self.arc.delete_volume(volumeID)
        self.arc.get_volume(volumeID)
