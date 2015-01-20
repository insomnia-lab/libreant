import json

from flask.ext.script import Manager

from webant import create_app

app = create_app()
manager = Manager(app)


@manager.option('-s', '--size', dest='size', required=False, default=-1,
                help='How many results to return. Defaults to all')
def db_export(size):
    '''outputs an exportable version of the db'''
    db = app.get_db()
    if int(size) < 0:
        size = len(db)
    for item in db.get_all_books(size=size)['hits']['hits']:
        print json.dumps(item)


@manager.command
def db_item_export(item_id):
    '''exports a single item'''
    db = app.get_db()
    book = db.get_book_by_id(item_id)
    print json.dumps(book)


@manager.command
def db_search(query):
    '''query, just like you would do in a browser'''
    db = app.get_db()
    res = db.user_search(query)['hits']['hits']
    for item in res:
        print json.dumps(item['_id'])


def main():
    manager.run()

if __name__ == '__main__':
    main()
