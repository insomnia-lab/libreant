from archivant.test import TestArchivant
from archivant.exceptions import NotFoundException
from nose.tools import raises, ok_, eq_
import os


class TestArchivantGetVolume(TestArchivant):

    @raises(NotFoundException)
    def test_get_volume_notexistent(self):
        self.arc.get_volume("unidchenonesiste")
        
    def test_get_volume(self):
        volume_metadata = self.generate_volume_metadata()
        id = self.arc.insert_volume(volume_metadata)
        self.arc.get_volume(id)

    def test_get_all_volumes(self):
        n = 3
        ids = list()
        for _ in range(n):
            id = self.arc.insert_volume(self.generate_volume_metadata())
            ids.append(id)
        self.arc._db.es.indices.refresh()
        volumes = [ vol for vol in self.arc.get_all_volumes()]
        for vol in volumes:
            ok_(vol['id'] in ids)
        eq_(len(volumes), len(ids))
