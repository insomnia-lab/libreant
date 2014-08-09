import json
import calendar
import datetime

import oursql


def json_default(obj):
    """Default JSON serializer. It solves the datetime problem"""
    if isinstance(obj, datetime.date):
        obj = datetime.datetime.fromordinal(obj.toordinal())
    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
    millis = int(
        calendar.timegm(obj.timetuple()) * 1000 +
        obj.microsecond / 1000
    )
    return millis


def canonize(row):
    '''
    Name of fields are not perfectly matching between rabbia and libreant.
    Let's fix it
    '''
    if 'author' in row:
        row['actors'] = [row['author']]
        del row['author']
    if 'type' in row:
        row['location'] = row['type']
        del row['type']
    return row


def db_to_json(connection):
    c = connection.cursor(oursql.DictCursor)
    c.execute('SELECT * FROM wp_rabbiaweblib_collection')

    for row in c:
        yield json.dumps(canonize(row), default=json_default)


def main():
    conn = oursql.connect(db='rabbia', user='root', passwd='root')
    with open('rabbia.json', 'w') as buf:
        for json_string in db_to_json(conn):
            buf.write(json_string + '\n')

if __name__ == '__main__':
    main()
