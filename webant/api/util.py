from flask import jsonify


class ApiError(Exception):
    def __init__(self, message, http_code, err_code=None, details=None):
        Exception.__init__(self, http_code, err_code, message, details)
        self.http_code = http_code
        self.err_code = err_code
        self.message = message
        self.details = details

    def __str__(self):
        return "http_code: {}, err_code: {}, message: '{}', details: '{}'".format(self.http_code, self.err_code, self.message, self.details)


def on_json_load_error(e):
    raise ApiError("Bad request", 400, details=str(e))


def make_success_response(message, http_code=200):
    response = jsonify({'code': http_code, 'message': message})
    response.status_code = http_code
    return response
