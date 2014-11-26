'''
read json books, one per line, and put them into elasticsearch
'''
from __future__ import print_function

import sys
import json

from libreantdb import DB
from elasticsearch import Elasticsearch

if __name__ == '__main__':
    db = DB(Elasticsearch())

    i = 0
    print("Loading...", end='')
    if len(sys.argv) > 1 and sys.argv[1] != '-':
        buf = open(sys.argv[1])
    else:
        buf = sys.stdin
    for line in buf:
        i += 1
        book = {'language': 'it'}
        book.update(json.loads(line))
        if i % 50:
            print("\rLoading\t%d" % i, end='')
        db.add_book(doc_type='book', body=book)
    print("\rDone\t(%d books added)" % i)
