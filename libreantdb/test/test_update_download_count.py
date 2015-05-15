from uuid import uuid4
from nose.tools import eq_, with_setup, raises
from elasticsearch import NotFoundError

from . import db, cleanall


def generate_book_body(attachments=0):
    body = {'title': 'La fine',
            '_language': 'it',
            '_attachments': []}
    for _ in range(attachments):
        attachment = {'id': uuid4().hex,
                      'name': 'foo',
                      'download_count': 0}
        body['_attachments'].append(attachment)
    return body


@raises(NotFoundError)
@with_setup(cleanall, cleanall)
def test_download_count_wrong_bookid():
    '''
    If we pass a wrong bookid to the increment function, an NotFoundError should be raised
    '''
    db.increment_download_count("wrong_bookID", uuid4())


@raises(NotFoundError)
@with_setup(cleanall, cleanall)
def test_download_count_wrong_attachmentid():
    '''
    If we pass a wrong attachmentID to the increment function, an NotFoundError should be raised
    '''
    bookID = db.add_book(body=generate_book_body(attachments=1))['_id']
    db.increment_download_count(bookID, uuid4())


@raises(Exception)
@with_setup(cleanall, cleanall)
def test_download_count_mandatory():
    '''
    if you omit the field download_count, increment_download_count will fail
    '''
    bookID = db.add_book(body=dict(title='La fine',
                                   _language='it',
                                   _attachments=[dict(name='foo')]
                                   ))['_id']
    db.increment_download_count(bookID, uuid4().hex)


@with_setup(cleanall, cleanall)
def test_update_download_count():
    body = generate_book_body(attachments=1)
    attachmentID = body['_attachments'][0]['id']
    bookID = db.add_book(body=body)['_id']
    for i in xrange(1, 5):
        db.increment_download_count(bookID, attachmentID)
        book = db.get_book_by_id(bookID)
        eq_(book['_source']['_attachments'][0]['download_count'], i)


@with_setup(cleanall, cleanall)
def test_update_download_count_no_other():
    ''' download count shouldn't modify other fields '''
    body = generate_book_body(attachments=1)
    attachmentID = body['_attachments'][0]['id']
    bookID = db.add_book(body=body)['_id']
    prev = db.get_book_by_id(bookID)
    db.increment_download_count(bookID, attachmentID)
    after = db.get_book_by_id(bookID)
    prev['_source']['_attachments'][0]['download_count'] += 1
    eq_(prev['_source'], after['_source'])
