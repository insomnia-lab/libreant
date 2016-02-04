import click
import logging
import json

from archivant import Archivant
from archivant.exceptions import NotFoundException
from conf import config_utils
from conf.defaults import get_def_conf, get_help
from utils.loggers import initLoggers
from custom_types import StringList


conf = dict()
arc = None


@click.group(name="libreant-db", help="command line program to manage libreant database")
@click.version_option()
@click.option('-s', '--settings', type=click.Path(exists=True, readable=True), help='file from which load settings')
@click.option('-d', '--debug', is_flag=True, help=get_help('DEBUG'))
@click.option('--fsdb-path', type=click.Path(), metavar="<path>", help=get_help('FSDB_PATH'))
@click.option('--es-indexname', type=click.STRING, metavar="<name>", help=get_help('ES_INDEXNAME'))
@click.option('--es-hosts', type=StringList(), metavar="<host>..", help=get_help('ES_HOSTS'))
def libreant_db(debug, settings, fsdb_path, es_indexname, es_hosts):
    initLoggers(logNames=['config_utils'])
    global conf
    conf = config_utils.load_configs('LIBREANT_', defaults=get_def_conf(), path=settings)
    cliConf = {}
    if debug:
        cliConf['DEBUG'] = True
    if fsdb_path:
        cliConf['FSDB_PATH'] = fsdb_path
    if es_indexname:
        cliConf['ES_INDEXNAME'] = es_indexname
    if es_hosts:
        cliConf['ES_HOSTS'] = es_hosts
    conf.update(cliConf)
    initLoggers(logging.DEBUG if conf.get('DEBUG', False) else logging.INFO)

    try:
        global arc
        arc = Archivant(conf=conf)
    except Exception as e:
        if conf.get('DEBUG', False):
            raise
        else:
            click.secho(str(e), fg='yellow', err=True)
            exit(1)


@libreant_db.command(name="export-volume", help="export a volume")
@click.argument('volumeid')
@click.option('-p', '--pretty', is_flag=True, help='format the output on multiple lines')
def export_volume(volumeid, pretty):
    try:
        volume = arc.get_volume(volumeid)
    except NotFoundException as e:
        click.secho(str(e), fg="yellow", err=True)
        exit(4)

    indent = 3 if pretty else None
    ouput = json.dumps(volume, indent=indent)
    click.echo(ouput)


@libreant_db.command(name="remove", help="remove a volume")
@click.argument('volumeid')
def delete_volume(volumeid):
    try:
        arc.delete_volume(volumeid)
    except NotFoundException as e:
        click.secho(str(e), fg="yellow", err=True)
        exit(4)


@libreant_db.command(help="search volumes by query")
@click.argument('query')
@click.option('-p', '--pretty', is_flag=True, help='format the output on multiple lines')
def search(query, pretty):
    results = arc._db.user_search(query)['hits']['hits']
    results = map(arc.normalize_volume, results)
    if not results:
        click.secho("No results found for '{}'".format(query), fg="yellow", err=True)
        exit(4)
    indent = 3 if pretty else None
    output = json.dumps(results, indent=indent)
    click.echo(output)


@libreant_db.command(name='export-all', help="export all volumes")
@click.option('-p', '--pretty', is_flag=True, help='format the output on multiple lines')
def export_all(pretty):
    indent = 3 if pretty else None
    volumes = [vol for vol in arc.get_all_volumes()]
    click.echo(json.dumps(volumes, indent=indent))


@libreant_db.command(name='append', help='append a file to an existing volume')
@click.argument('volumeid')
@click.option('-f', 'filepath', type=click.Path(exists=True,resolve_path=True), multiple=True, help='the path to the media to be uploaded')
@click.option('-n', '--name', type=click.STRING, metavar='<file.ext>', multiple=True, help='name of the file, including the extension')
@click.option('-m', '--mime', type=click.STRING, metavar='<group>/<type>', multiple=True, help='mime type of the media')
@click.option('-t', '--notes', type=click.STRING, metavar='<string>', multiple=True, help='notes about the media')
def append_file(volumeid,filepath,name,mime,notes):
    attachments = attach_list(filepath, name, mime, notes)
    try:
        arc.insert_attachments(volumeid,attachments)
    except:
        click.secho('An upload error occurred in updating an attachment!',fg='yellow', err=True)
        exit(4)


@libreant_db.command(name='insert-volume', help='creates an item in the db')
@click.option('-l', '--language', type=click.STRING, required=True, help='specify the language of the media you are going to upload')
@click.option('-f', '--filepath', type=click.Path(exists=True,resolve_path=True), multiple=True, help='path to the media to be uploaded')
@click.option('-n', '--name', type=click.STRING, metavar='<file.ext>', multiple=True, help='filename (once uploaded)')
@click.option('-m', '--mime', type=click.STRING, metavar='<group>/<type>', multiple=True, help='mime type of the media')
@click.option('-t', '--notes', type=click.STRING, metavar='<a string about the file>', multiple=True, help='notes about the media')
@click.option('-e', '--metadata', type=click.STRING, metavar='{"title":"Ulysses", "actors":["joyce", "beach"],...}', help='all the metadata')
def insert_volume(language,filepath,name,mime,notes,metadata):
    meta = {"_language":language}
    if metadata:
        meta.update(json.loads(metadata))
    attachments = attach_list(filepath, name, mime, notes)
    try:
        out = arc.insert_volume(meta,attachments)
    except:
        click.secho('An upload error have occurred!', fg="yellow", err=True)
        exit(4)
    click.echo(out)


def attach_list(filepaths, names, mimes, notes):
    '''
    all the arguments are lists
    returns a list of dictionaries; each dictionary "represent" an attachment
    '''
    assert type(filepaths) in (list, tuple)
    assert type(names) in (list, tuple)
    assert type(mimes) in (list, tuple)
    assert type(notes) in (list, tuple)

    if [len(l)
        for l in (filepaths, names, mimes, notes)
        ].count(len(filepaths)) != 4:  # which means "if their length is not the same for everyone"
        click.secho('The number of --filepath, --names, --mime and -note '
                    'should be the same')
        exit(2)

    attach_list = []
    for fname, name, mime, note in zip(filepaths, names, mimes, notes):
        attach_list.append({
            'file': fname,
            'name': name,
            'mime': mime,
            'note': note
        })
    return attach_list


if __name__ == '__main__':
    libreant_db()
