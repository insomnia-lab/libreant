'''
read json books, one per line, and put them into elasticsearch
'''

import sys
import json

from libreantdb import DB
from elasticsearch import Elasticsearch

if __name__ == '__main__':
    db = DB(Elasticsearch())

    i = 0
    print "Loading...",
    for line in open(sys.argv[1]):
        i += 1
        book = {'language': 'it'}
        book.update(json.loads(line))
        if i % 50:
            print "\rLoading\t%d" % i,
        db.add_book(doc_type='book', body=book)
    print "\rDone\t%d" % i
