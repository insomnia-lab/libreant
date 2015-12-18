from passlib.hash import pbkdf2_sha256

defConf = {
  'DEBUG':        (False, "operate in debug mode"),
  'PORT':         (5000, "port on which daemon will listen"),
  'ADDRESS':      ("0.0.0.0", "address on which daemon will listen"),
  'FSDB_PATH':    (None, "path used for storing binary files"),
  'ES_INDEXNAME': ('libreant', "index name to use for elasticsearch"),
  'ES_HOSTS':     (None, "list of elasticsearch nodes to connect to"),
  'PRESET_PATHS': ([], "list of paths where to look for presets definition"),
  'AGHERANT_DESCRIPTIONS': (None, "list of description urls of nodes to aggregate"),
  'BOOTSTRAP_SERVE_LOCAL': (True, "decide to serve bootstrap related files as local content"),
  'MAX_RESULTS_PER_PAGE': (50, "number of max results for one request"),
  'USERS_DATABASE': (None, "url of the database used for users managment"),
  'PWD_SALT_SIZE': (16, "size of the salt used by password hashing algorithm"),
  'PWD_ROUNDS': (pbkdf2_sha256.default_rounds, "number of rounds runs by password hashing algorithm")
}


def get_def_conf():
    '''return default configurations as simple dict'''
    ret = dict()
    for k,v in defConf.items():
        ret[k] = v[0]
    return ret


def get_help(conf):
    '''return the help message of a specific configuration parameter'''
    return defConf[conf][1]
