from archivant.test import TestArchivant

from nose.tools import raises, ok_, eq_


class TestArchivantShrink(TestArchivant):

    def test_dangling_files_db_empty(self):
        '''no dangling files with db empty'''
        eq_(len([fid for fid in self.arc.dangling_files()]), 0)

    def test_dangling_files_empty(self):
        '''no dangling files without previous deletion'''
        n = 3
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(n)
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        self.arc._db.es.indices.refresh()
        eq_(len([fid for fid in self.arc.dangling_files()]), 0)

    def test_dangling_files(self):
        n = 3
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(n)
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        self.arc.delete_volume(id)
        self.arc._db.es.indices.refresh()
        eq_(len([fid for fid in self.arc.dangling_files()]), n)

    def test_shrink_dangling(self):
        n = 3
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(n)
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        self.arc.delete_volume(id)
        self.arc._db.es.indices.refresh()
        eq_(self.arc.shrink_local_fsdb(dangling=True), n)
        eq_(len(self.arc._fsdb), 0)

    def test_shrink_dryrun(self):
        n = 3
        volume_metadata = self.generate_volume_metadata()
        attachments = self.generate_attachments(n)
        id = self.arc.insert_volume(volume_metadata, attachments=attachments)
        self.arc.delete_volume(id)
        self.arc._db.es.indices.refresh()
        eq_(self.arc.shrink_local_fsdb(dangling=True, dryrun=True), n)
        eq_(len(self.arc._fsdb), n)
