import click
import logging
import json

from conf import config_utils
from conf.defaults import get_def_conf, get_help
from utils.loggers import initLoggers
from webant.webant import main
from custom_types import StringList


@click.command(help="launch libreant daemon")
@click.version_option()
@click.option('-s', '--settings', type=click.Path(exists=True, readable=True), metavar="<path>", help='file from wich load settings')
@click.option('-d', '--debug', is_flag=True, help=get_help('DEBUG'))
@click.option('-p', '--port', type=click.IntRange(min=1, max=65535), metavar="<port>", help=get_help('PORT'))
@click.option('--address', type=click.STRING, metavar="<address>", help=get_help('ADDRESS'))
@click.option('--fsdb-path', type=click.Path(), metavar="<path>", help=get_help('FSDB_PATH'))
@click.option('--es-indexname', type=click.STRING, metavar="<name>", help=get_help('ES_INDEXNAME'))
@click.option('--es-hosts', type=StringList(), metavar="<host>..", help=get_help('ES_HOSTS'))
@click.option('--users-db', type=click.Path(), metavar="<url>", help=get_help('USERS_DATABASE') )
@click.option('--preset-paths', type=StringList(), metavar="<path>..", help=get_help('PRESET_PATHS'))
@click.option('--agherant-descriptions', type=StringList(), metavar="<url>..", help=get_help('AGHERANT_DESCRIPTIONS'))
@click.option('--dump-settings', is_flag=True, help='dump current settings and exit')
def libreant(settings, debug, port, address, fsdb_path, es_indexname, es_hosts, users_db, preset_paths, agherant_descriptions, dump_settings):
    initLoggers(logNames=['config_utils'])
    conf = config_utils.load_configs('LIBREANT_', defaults=get_def_conf(), path=settings)
    cliConf = {}
    if debug:
        cliConf['DEBUG'] = True
    if port:
        cliConf['PORT'] = port
    if address:
        cliConf['ADDRESS'] = address
    if fsdb_path:
        cliConf['FSDB_PATH'] = fsdb_path
    if es_indexname:
        cliConf['ES_INDEXNAME'] = es_indexname
    if es_hosts:
        cliConf['ES_HOSTS'] = es_hosts
    if users_db:
        cliConf['USERS_DATABASE'] = users_db
    if preset_paths:
        cliConf['PRESET_PATHS'] = preset_paths
    if agherant_descriptions:
        cliConf['AGHERANT_DESCRIPTIONS'] = agherant_descriptions
    conf.update(cliConf)

    if dump_settings:
        click.echo(json.dumps(conf, indent=3))
        exit(0)

    initLoggers(logging.DEBUG if conf.get('DEBUG', False) else logging.WARNING)
    try:
        main(conf)
    except Exception as e:
        if conf.get('DEBUG', False):
            raise
        else:
            click.secho(str(e), fg='yellow', err=True)
            exit(1)

if __name__ == '__main__':
    libreant()
