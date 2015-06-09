import click
import logging

from utils import config_utils
from utils.loggers import initLoggers
from webant.webant import main
from custom_types import StringList

@click.command(help="launch libreant daemon")
@click.version_option()
@click.option('-s', '--settings', type=click.Path(exists=True, readable=True), metavar="<path>", help='file from wich load settings')
@click.option('-d', '--debug', is_flag=True, help='operate in debug mode')
@click.option('-p', '--port', type=click.IntRange(min=1, max=65535), metavar="<port>", help='port on which daemon will listen')
@click.option('--address', type=click.STRING, metavar="<address>", help='address on which daemon will listen')
@click.option('--fsdb-path', type=click.Path(), metavar="<path>", help='path used for storing binary file')
@click.option('--es-indexname', type=click.STRING, metavar="<name>", help='index name to use for elasticsearch')
@click.option('--es-hosts', type=StringList(), metavar="<host>..", help='list of elasticsearch nodes to connect to')
@click.option('--preset-paths', type=StringList(), metavar="<path>..", help='list of paths where to look for presets')
@click.option('--agherant-descriptions', type=StringList(), metavar="<url>..", help='list of description urls of nodes to aggregate')
def libreant(settings, debug, port, address, fsdb_path, es_indexname, es_hosts, preset_paths, agherant_descriptions):
    initLoggers(logNames=['config_utils'])
    conf = config_utils.load_configs('LIBREANT_', path=settings)
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
    if preset_paths:
        cliConf['PRESET_PATHS'] = preset_paths
    if agherant_descriptions:
        cliConf['AGHERANT_DESCRIPTIONS'] = agherant_descriptions
    conf.update(cliConf)
    initLoggers(logging.DEBUG if conf.get('DEBUG', False) else logging.WARNING)
    try:
        main(conf)
    except Exception as e:
        if conf.get('DEBUG', False):
            raise
        else:
            click.secho(str(e), fg='yellow', err=True)

if __name__ == '__main__':
    libreant()
