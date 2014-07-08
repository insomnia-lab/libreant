from couchdb.mapping import Document, TextField, ListField

from . import get_db


class Book(Document):
    title = TextField()
    description = TextField()
    authors = ListField(TextField)
