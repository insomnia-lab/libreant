from __future__ import print_function

import os
import json
from logging import getLogger
log = getLogger('config_utils')


def from_envvar_file(envvar, environ=None):
    if environ is None:
        environ = os.environ
    if envvar not in environ:
        return {}
    fname = environ[envvar]
    if not os.path.exists(fname):
        log.debug('config file does not exist')
        return {}
    try:
        with open(fname) as buf:
            conf = json.load(buf)
            return conf
    except Exception:
        log.warning('Error loading config file from envvar', exc_info=1)
        return {}


def from_envvars(prefix=None, environ=None, envvars=None, as_json=True):
    """Load environment variables in a dictionary

    Values are parsed as JSON. If parsing fails with a ValueError,
    values are instead used as verbatim strings.

    :param prefix: If ``None`` is passed as envvars, all variables from
                   ``environ`` starting with this prefix are imported. The
                   prefix is stripped upon import.
    :param envvars: A dictionary of mappings of environment-variable-names
                    to Flask configuration names. If a list is passed
                    instead, names are mapped 1:1. If ``None``, see prefix
                    argument.
    :param environ: use this dictionary instead of os.environ; this is here
                    mostly for mockability
    :param as_json: If False, values will not be parsed as JSON first.
    """
    conf = {}
    if environ is None:
        environ = os.environ
    if prefix is None and envvars is None:
        raise RuntimeError('Must either give prefix or envvars argument')

    # if it's a list, convert to dict
    if isinstance(envvars, list):
        envvars = {k: k for k in envvars}

    if not envvars:
        envvars = {k: k[len(prefix):] for k in environ.keys()
                   if k.startswith(prefix)}

    for env_name, name in envvars.items():
        if env_name not in environ:
            continue

        if as_json:
            try:
                conf[name] = json.loads(environ[env_name])
            except ValueError:
                conf[name] = environ[env_name]
        else:
            conf[name] = environ[env_name]

    return conf
