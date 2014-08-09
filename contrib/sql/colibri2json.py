import json
import calendar
import datetime
import decimal

import oursql


def json_default(obj):
    """Default JSON serializer. It solves the datetime problem"""
    if isinstance(obj, datetime.date):
        obj = datetime.datetime.fromordinal(obj.toordinal())
    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
    if isinstance(obj, decimal.Decimal):
        if int(obj) == 0:
            return None
        obj = datetime.datetime(day=1, month=1, year=int(obj))
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
    row['title'] = row['titolo']
    del row['titolo']

    row['actors'] = filter(bool,  # exclude empty strings
                           row['autore'].split(',') +
                           row['editore'].split(','))
    del row['autore']
    del row['editore']

    row['location'] = '%s - %s' % (row['descrizione'], row['nome'])
    del row['descrizione']
    del row['nome']
    del row['ID_LOC']
    del row['IDB']

    del row['ID_LIBRO']
    del row['prestabilita']
    if row['ISBN']:
        row['isbn'] = row['ISBN']
    del row['ISBN']
    if not row['note']:
        del row['note']
    return row


def db_to_json(connection):
    c = connection.cursor(oursql.DictCursor)
    c.execute('SELECT * FROM libri ' +
              'NATURAL JOIN lib_biblio NATURAL JOIN biblioteche')

    for row in c:
        yield json.dumps(canonize(row), default=json_default)


def main():
    conn = oursql.connect(db='colibri', user='root', passwd='root')
    with open('colibri.json', 'w') as buf:
        for json_string in db_to_json(conn):
            buf.write(json_string + '\n')

if __name__ == '__main__':
    main()
