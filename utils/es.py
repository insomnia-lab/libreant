from elasticsearch import Elasticsearch as Elasticsearch_official
from elasticsearch import __version__ as es_pylib_version


def Elasticsearch(*args, **kwargs):
    """Elasticsearch wrapper function

    Wrapper function around the official Elasticsearch class that adds
    a simple version check upon initialization.
    In particular it checks if the major version of the library in use
    match the one of the cluster that we are tring to interact with.
    The check can be skipped by setting to false the check_version parameter.

    #note: Boyska didn't like subclassing :)
    """
    check_version = kwargs.pop('check_version', True)
    es = Elasticsearch_official(*args, **kwargs)
    if check_version:
        es_version = es.info()['version']['number'].split('.')
        if(int(es_version[0]) != int(es_pylib_version[0])):
            raise RuntimeError("The Elasticsearch python library version does not match the one of the running cluster: {} != {}. Please install the correct elasticsearch-py version".format(es_pylib_version[0], es_version[0]))
    return es
