'''
Get a CSV (tab-delimited) where columns are:
1) # of items
2) Authors, comma delimited
3) Title
4) Publisher
'''
import sys
import csv
import json


if __name__ == '__main__':
    csvpath = sys.argv[1]
    reader = csv.reader(open(csvpath, 'rb'), delimiter=',', quotechar='"')
    for line in reader:
        line += [''] * (6 - len(line))
        line = map(lambda s: s.decode('latin1'), line)
        numloc, authors, title, date, collana, editor = line[:6]
        loc = ' '.join(numloc.split()[1:])
        book = {
            'location': loc,
            'title': title,
            'actors': authors.split('-') + [editor],
            'pubYear': date,
            'collana': collana
        }
        print json.dumps(book)


# vim: set ts=4 sw=4 et:
