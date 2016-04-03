from flask import Blueprint, current_app, jsonify
from webant.util import add_routes
from util import ApiError
from archivant_api import routes as archivantRoutes
from users_api import routes as usersRoutes


def get_blueprint_api(archivant_routes=True,
                      users_routes=True):
    api = Blueprint('api', __name__)
    if archivant_routes:
        add_routes(api, archivantRoutes)
    if users_routes:
        add_routes(api, usersRoutes)

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

    return api
