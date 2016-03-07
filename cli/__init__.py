import click
import sys
from conf.config_utils import load_configs


def die(msg, exit_code=1, error=True):
    ce = click.ClickException(click.style(msg, fg='red'))
    ce.exit_code = exit_code
    raise ce


def bye(msg, exit_code=1, fg='yellow'):
    click.secho(msg, fg=fg)
    sys.exit(exit_code)


def load_cfg(path, envvar_prefix='LIBREANT_', debug=False):
    '''wrapper of config_utils.load_configs'''
    try:
        return load_configs(envvar_prefix, path=path)
    except Exception as e:
        if debug:
            raise
        else:
            die(str(e))
