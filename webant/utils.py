import functools


def memoize(obj):
    '''decorator to memoize things'''
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer

def requestedFormat(request,acceptedFormat):
        """Return the response format requested by client

        Client could specify requested format using:
        (options are processed in this order)
            - `format` field in http request
            - `Accept` header in http request
        Example:
            chooseFormat(request, ['text/html','application/json'])
        Args:
            acceptedFormat: list containing all the accepted format
        Returns:
            string: the user requested mime-type (if supported)
        Raises:
            ValueError: if user request a mime-type not supported
        """
        if 'format' in request.args:
            fieldFormat = request.args.get('format')
            if fieldFormat not in acceptedFormat:
                raise ValueError("requested format not supported: "+ fieldFormat)
            return fieldFormat
        else:
            return request.accept_mimetypes.best_match(acceptedFormat)
