from __future__ import print_function
import sys
import json
import logging

from flask.ext.script import Manager

from webant import LibreantCoreApp, initLoggers
import config_utils

initLoggers()
conf = {'DEBUG': True}
conf.update(config_utils.from_envvar_file('WEBANT_SETTINGS'))
conf.update(config_utils.from_envvars(prefix='WEBANT_'))
initLoggers(logging.DEBUG if conf.get('DEBUG', False) else logging.WARNING)
app = LibreantCoreApp('webant', conf)
manager = Manager(app)


@manager.option('-s', '--size', dest='size', required=False, default=-1,
                help='How many results to return. Defaults to all')
def db_export(size):
    '''outputs an exportable version of the db'''
    db = app.get_db()
    if int(size) < 0:
        size = len(db)
    for item in db.get_all_books(size=size)['hits']['hits']:
        print(json.dumps(item))


@manager.command
def db_item_export(item_id):
    '''exports a single item'''
    db = app.get_db()
    book = db.get_book_by_id(item_id)
    print(json.dumps(book))


@manager.command
def db_search(query):
    '''query, just like you would do in a browser'''
    db = app.get_db()
    res = db.user_search(query)['hits']['hits']
    for item in res:
        print(item['_id'])


@manager.option('filename',
                help='File to read from, or stdin if "-" is provided')
def db_import(filename, language='it'):
    '''imports items from a previous export'''
    if filename == '-':
        buf = sys.stdin
    else:
        buf = open(filename)
    db = app.get_db()
    i = 0
    for line in buf:
        i += 1
        book = json.loads(line)
        if '_source' in book:
            book = book['_source']
        if '_language' not in book:
            book['_language'] = language

        if i % 50:
            print("\rLoading\t%d" % i, end='')
        db.add_book(doc_type='book', body=book)
    print("\r" + " "*30, end='')
    print("\rDone\t(%d books added)" % i)


@manager.command
def conf_list():
    '''List every key,value pair in configuration'''
    for key, value in app.config.items():
        print('{}: {}'.format(key, value))


@manager.command
def conf_show(key):
    '''Show the value for a given configuration key'''
    if key in app.config:
        print(app.config[key])
        return 0
    else:
        print('Cannot find such option')
        return 1


def main():
    manager.run()

if __name__ == '__main__':
    main()
