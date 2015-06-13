from flask import Blueprint, current_app, jsonify
from archivant.exceptions import NotFoundException


class ApiError(Exception):
    def __init__(self, message, http_code, err_code=None, details=None):
        Exception.__init__(self, http_code, err_code, message, details)
        self.http_code = http_code
        self.err_code = err_code
        self.message = message
        self.details = details

    def __str__(self):
        return "http_code: {}, err_code: {}, message: '{}', details: '{}'".format(self.http_code, self.err_code, self.message, self.details)


api = Blueprint('api', __name__)

@api.errorhandler(ApiError)
def apiErrorHandler(apiErr):
    error = {}
    error['code'] = apiErr.err_code if (apiErr.err_code is not None) else apiErr.http_code
    error['message'] = apiErr.message
    error['details'] = apiErr.details if (apiErr.details is not None) else ""

    response = jsonify({'error': error})
    response.status_code = apiErr.http_code
    return response

# workaround for "https://github.com/mitsuhiko/flask/issues/1498"
@api.route("/<path:invalid_path>", methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])
def apiNotFound(invalid_path):
    raise ApiError("invalid URI", 404)

@api.errorhandler(Exception)
def exceptionHandler(e):
    current_app.logger.exception(e)
    return apiErrorHandler(ApiError("internal server error", 500))
