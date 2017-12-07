from elasticsearch import Elasticsearch as Elasticsearch_official
from elasticsearch import __version__ as es_pylib_version


class Elasticsearch(Elasticsearch_official):
    """Elasticsearch wrapper class

    Wrapper class around the official Elasticsearch class that adds
    a simple version check upon initialization.
    In particular it checks if the major version of the library in use
    match the one of the cluster that we are tring to interact with.
    The check can be skipped by setting to false the check_version parameter.
    """

    def __init__(self, check_version=True, *args, **kargs):
        super(Elasticsearch, self).__init__(*args, **kargs)
        if check_version:
            es_version = self.get_version()
            if(int(es_version[0]) != int(es_pylib_version[0])):
                raise RuntimeError("The Elasticsearch python library version does not match the one of the running cluster: {} != {}. Please install the correct elasticsearch-py version".format(es_pylib_version[0], es_version[0]))

    def get_version(self):
        return self.info()['version']['number'].split('.')
