import os.path
from tempfile import mkdtemp
from unittest import TestCase
from shutil import rmtree

from nose.tools import eq_, raises
import click

from cli.libreant_db import attach_list


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

    @raises(click.BadOptionUsage)
    def test_length_no_notes(self):
        attach_list([self.generate('foo')], [])

    @raises(click.BadOptionUsage)
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
