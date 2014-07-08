from couchdb.design import ViewDefinition
import sys


# Stolen from http://markhaase.com/2012/06/23/couchdb-views-in-python/
class CouchView(ViewDefinition):
    """
    A base class for couch views that handles the magic of instantiation.
    """
    defaults = {}

    def __init__(self):
        """
        Does some magic to map the subclass implementation into the format
        expected by ViewDefinition.
        """

        module = sys.modules[self.__module__]
        design_name = module.__name__.split('.')[-1]

        if hasattr(self.__class__, "map"):
            map_fun = self.__class__.map
        else:
            raise NotImplementedError("Couch views require a map() method.")

        if hasattr(self.__class__, "reduce"):
            reduce_fun = self.__class__.reduce
        else:
            reduce_fun = None

        defaults = self.__class__.defaults
        print 'Run %s with def %s' % (self.__class__.__name__, str(defaults))
        super(CouchView, self).__init__(design_name, self.__class__.__name__,
                                        map_fun, reduce_fun,
                                        language='python', **defaults)
