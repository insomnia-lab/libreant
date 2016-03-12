import os.path
from tempfile import mkdtemp
from unittest import TestCase
from shutil import rmtree
import json

from nose.tools import eq_, raises
import click
import click.testing
from elasticsearch import Elasticsearch

from cli.libreant_db import attach_list, libreant_db


class TestAttachList(TestCase):
    def setUp(self):
        self.tmpdir = mkdtemp(prefix=self.__class__.__name__)

    def tearDown(self):
        rmtree(self.tmpdir)

    def generate(self, fname):
        '''helper function: create a temporary file, and return its path'''
        fpath = os.path.join(self.tmpdir, fname)
        open(fpath, 'w').close()
        return fpath

    def test_empty(self):
        eq_(len(attach_list([], [])), 0)

    @raises(click.ClickException)
    def test_length_no_notes(self):
        attach_list([self.generate('foo')], [])

    @raises(click.ClickException)
    def test_length_too_many_notes(self):
        attach_list([], ['mynote'])

    def test_no_mime(self):
        attachments = attach_list([self.generate('foo')], ['mynote'])
        eq_(len(attachments), 1)
        eq_(attachments[0]['mime'], None)

    def test_pdf(self):
        attachments = attach_list([self.generate('a.pdf')], ['mynote'])
        eq_(len(attachments), 1)
        eq_(attachments[0]['mime'], 'application/pdf')


class TestDedicatedEs(TestCase):
    def setUp(self):
        self.fsdbPath = mkdtemp(prefix=self.__class__.__name__ +
                            '_fsdb_')
        self.cli = click.testing.CliRunner(env={
            'LIBREANT_FSDB_PATH': self.fsdbPath,
            'LIBREANT_ES_INDEXNAME': 'test-book'
        })

    def tearDown(self):
        es = Elasticsearch()
        if es.indices.exists('test-book'):
            es.indices.delete('test-book')
        rmtree(self.fsdbPath)


class TestSearch(TestDedicatedEs):
    def test_search_doesnotexist(self):
        res = self.cli.invoke(libreant_db, ('search', 'notexisting'))
        assert res.exit_code != 0


class TestInsert(TestDedicatedEs):
    def setUp(self):
        super(TestInsert, self).setUp()
        self.tmpdir = mkdtemp(prefix=self.__class__.__name__)

    def tearDown(self):
        super(TestInsert, self).tearDown()
        rmtree(self.tmpdir)

    def generate(self, fname, content=None):
        '''helper function: create a temporary file, and return its path'''
        fpath = os.path.join(self.tmpdir, fname)
        buf = open(fpath, 'w')
        if content is not None:
            json.dump(content, buf)
        buf.close()
        return fpath

    def test_no_metadata(self):
        res = self.cli.invoke(libreant_db, ('insert-volume', '-l', 'en'))
        assert res.exit_code != 0

    def test_no_language(self):
        '''--language is required'''
        res = self.cli.invoke(libreant_db, ('insert-volume',
                                            self.generate('meta.json')))
        assert res.exit_code != 0
        assert '--language' in res.output

    def test_empty(self):
        '''adding empty book'''
        meta = self.generate('m.json', {})
        res = self.cli.invoke(libreant_db, ('insert-volume', '-l', 'en',
                                            meta))
        eq_(res.exit_code, 0)

    def test_real_metadata(self):
        meta = self.generate('m.json', dict(
            title='Some title',
            actors=['me', 'myself']
        ))
        res = self.cli.invoke(libreant_db, ('insert-volume', '-l', 'en',
                                            meta))
        eq_(res.exit_code, 0)
        vid = [line for line in res.output.split('\n')
               if line.strip()][-1].strip()
        export_res = self.cli.invoke(libreant_db, ('export-volume', vid))
        eq_(export_res.exit_code, 0)
        volume_data = json.loads(export_res.output)
        eq_(volume_data['metadata']['title'], 'Some title')

    def test_attach(self):
        meta = self.generate('m.json', {})
        res = self.cli.invoke(libreant_db, ('insert-volume', '-l', 'en',
                                            meta))
        eq_(res.exit_code, 0)
        vid = [line for line in res.output.split('\n')
               if line.strip()][-1].strip()
        attach_res = self.cli.invoke(libreant_db,
                                     ('attach', '-f', self.generate('empty'),
                                      '--notes', 'somenote', vid))
        eq_(attach_res.exit_code, 0)
        export_res = self.cli.invoke(libreant_db, ('export-volume', vid))
        eq_(export_res.exit_code, 0)
        volume_data = json.loads(export_res.output)
        eq_(len(volume_data['attachments']), 1)
        eq_(volume_data['attachments'][0]['metadata']['name'], 'empty')
