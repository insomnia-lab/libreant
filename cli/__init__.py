import click
from conf.config_utils import load_configs


def load_cfg(path, envvar_prefix='LIBREANT_', debug=False):
    '''wrapper of config_utils.load_configs'''
    try:
        return load_configs(envvar_prefix, path=path)
    except Exception as e:
        if debug:
            raise
        else:
            raise click.ClickException(click.style(str(e), fg='red'))
