from flask import Blueprint, current_app, jsonify, request, url_for

from archivant.archivant import Archivant
from archivant.exceptions import NotFoundException
from webant.utils import send_attachment_file


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


@api.route('/volumes/')
def get_volumes():
    q = request.args.get('q', "*:*")
    try:
        from_ = int(request.args.get('from', 0))
    except ValueError, e:
        raise ApiError("Bad Request", 400, details="could not covert 'from' parameter to number")
    try:
        size = int(request.args.get('size', 10))
    except ValueError, e:
        raise ApiError("Bad Request", 400, details="could not covert 'size' parameter to number")
    if size > current_app.config.get('MAX_RESULTS_PER_PAGE', 50):
        raise ApiError("Request Entity Too Large", 413, details="'size' parameter is too high")

    q_res = current_app.archivant._db.get_books_querystring(query=q, from_=from_, size=size)
    volumes = map(Archivant.normalize_volume, q_res['hits']['hits'])
    next_args = "?q={}&from={}&size={}".format(q, from_ + size, size)
    prev_args = "?q={}&from={}&size={}".format(q, from_ - size if ((from_ - size) > -1) else 0, size)
    base_url = url_for('.get_volumes', _external=True)
    res = {'link_prev': base_url + prev_args,
           'link_next': base_url + next_args,
           'total': q_res['hits']['total'],
           'data': volumes}
    return jsonify(res)

@api.route('/volumes/<volumeID>', methods=['GET'])
def get_volume(volumeID):
    try:
        volume = current_app.archivant.get_volume(volumeID)
    except NotFoundException, e:
        raise ApiError("volume not found", 404, details=str(e))
    return jsonify({'data': volume})

@api.route('/volumes/<volumeID>/attachments/', methods=['GET'])
def get_attachments(volumeID):
    try:
        atts = current_app.archivant.get_volume(volumeID)['attachments']
    except NotFoundException, e:
        raise ApiError("volume not found", 404, details=str(e))
    return jsonify({'data': atts})

@api.route('/volumes/<volumeID>/attachments/<attachmentID>', methods=['GET'])
def get_attachment(volumeID, attachmentID):
    try:
        att = current_app.archivant.get_attachment(volumeID, attachmentID)
    except NotFoundException, e:
        raise ApiError("attachment not found", 404, details=str(e))
    return jsonify({'data': att})

@api.route('/volumes/<volumeID>/attachments/<attachmentID>/file', methods=['GET'])
def get_file(volumeID, attachmentID):
    try:
        return send_attachment_file(current_app.archivant, volumeID, attachmentID)
    except NotFoundException, e:
        raise ApiError("file not found", 404, details=str(e))
