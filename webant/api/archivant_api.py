import json
import tempfile
import os
from werkzeug import secure_filename
from webant.util import send_attachment_file, routes_collector
from flask import request, current_app, url_for, jsonify
from archivant import Archivant
from archivant.exceptions import NotFoundException
from util import ApiError, make_success_response


routes = []
route = routes_collector(routes)


@route('/volumes/')
def get_volumes():
    q = request.args.get('q', "*:*")
    try:
        from_ = int(request.args.get('from', 0))
    except ValueError:
        raise ApiError("Bad Request", 400, details="could not covert 'from' parameter to number")
    try:
        size = int(request.args.get('size', 10))
    except ValueError:
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


@route('/volumes/', methods=['POST'])
def add_volume():
    metadata = receive_volume_metadata()
    try:
        volumeID = current_app.archivant.insert_volume(metadata)
    except ValueError, e:
        raise ApiError("malformed metadata", 400, details=str(e))
    link_self = url_for('.get_volume', volumeID=volumeID, _external=True)
    response = jsonify({'data': {'id': volumeID, 'link_self': link_self}})
    response.status_code = 201
    response.headers['Location'] = link_self
    return response


@route('/volumes/<volumeID>', methods=['PUT'])
def update_volume(volumeID):
    metadata = receive_volume_metadata()
    try:
        current_app.archivant.update_volume(volumeID, metadata)
    except NotFoundException, e:
        raise ApiError("volume not found", 404, details=str(e))
    except ValueError, e:
        raise ApiError("malformed metadata", 400, details=str(e))
    return make_success_response("volume successfully updated", 201)


@route('/volumes/<volumeID>', methods=['GET'])
def get_volume(volumeID):
    try:
        volume = current_app.archivant.get_volume(volumeID)
    except NotFoundException, e:
        raise ApiError("volume not found", 404, details=str(e))
    return jsonify({'data': volume})


@route('/volumes/<volumeID>', methods=['DELETE'])
def delete_volume(volumeID):
    try:
        current_app.archivant.delete_volume(volumeID)
    except NotFoundException, e:
        raise ApiError("volume not found", 404, details=str(e))
    return make_success_response("volume has been successfully deleted")


@route('/volumes/<volumeID>/attachments/', methods=['GET'])
def get_attachments(volumeID):
    try:
        atts = current_app.archivant.get_volume(volumeID)['attachments']
    except NotFoundException, e:
        raise ApiError("volume not found", 404, details=str(e))
    return jsonify({'data': atts})


@route('/volumes/<volumeID>/attachments/', methods=['POST'])
def add_attachments(volumeID):
    metadata = receive_metadata(optional=True)
    if 'file' not in request.files:
        raise ApiError("malformed request", 400, details="file not found under 'file' key")
    upFile = request.files['file']
    tmpFileFd, tmpFilePath = tempfile.mkstemp()
    upFile.save(tmpFilePath)
    fileInfo = {}
    fileInfo['file'] = tmpFilePath
    fileInfo['name'] = secure_filename(upFile.filename)
    fileInfo['mime'] = upFile.mimetype
    fileInfo['notes'] = metadata.get('notes', '')
    # close fileDescriptor
    os.close(tmpFileFd)
    try:
        attachmentID = current_app.archivant.insert_attachments(volumeID, attachments=[fileInfo])[0]
    except NotFoundException, e:
        raise ApiError("volume not found", 404, details=str(e))
    finally:
        # remove temp files
        os.remove(fileInfo['file'])
    link_self = url_for('.get_attachment', volumeID=volumeID, attachmentID=attachmentID, _external=True)
    response = jsonify({'data': {'id': attachmentID, 'link_self': link_self}})
    response.status_code = 201
    response.headers['Location'] = link_self
    return response


@route('/volumes/<volumeID>/attachments/<attachmentID>', methods=['GET'])
def get_attachment(volumeID, attachmentID):
    try:
        att = current_app.archivant.get_attachment(volumeID, attachmentID)
    except NotFoundException, e:
        raise ApiError("attachment not found", 404, details=str(e))
    return jsonify({'data': att})


@route('/volumes/<volumeID>/attachments/<attachmentID>', methods=['DELETE'])
def delete_attachment(volumeID, attachmentID):
    try:
        current_app.archivant.delete_attachments(volumeID, [attachmentID])
    except NotFoundException, e:
        raise ApiError("attachment not found", 404, details=str(e))
    return make_success_response("attachment has been successfully deleted")


@route('/volumes/<volumeID>/attachments/<attachmentID>', methods=['PUT'])
def update_attachment(volumeID, attachmentID):
    metadata = receive_metadata()
    try:
        current_app.archivant.update_attachment(volumeID, attachmentID, metadata)
    except ValueError, e:
        raise ApiError("malformed request", 400, details=str(e))
    return make_success_response("attachment has been successfully updated")


@route('/volumes/<volumeID>/attachments/<attachmentID>/file', methods=['GET'])
def get_file(volumeID, attachmentID):
    try:
        return send_attachment_file(current_app.archivant, volumeID, attachmentID)
    except NotFoundException, e:
        raise ApiError("file not found", 404, details=str(e))


def receive_volume_metadata():
    metadata = receive_metadata()
    # TODO check also for preset consistency?
    requiredFields = ['_language']
    for requiredField in requiredFields:
        if requiredField not in metadata:
            raise ApiError("malformed metadata", 400, details="Required field '{}' is missing in metadata".format(requiredField))
    return metadata


def receive_metadata(optional=False):
    if optional and 'metdata' not in request.values:
        return {}
    try:
        metadata = json.loads(request.values['metadata'])
    except KeyError:
        raise ApiError("malformed request", 400, details="missing 'metadata' in request")
    except Exception, e:
        raise ApiError("malformed metadata", 400, details=str(e))
    if not isinstance(metadata, dict):
        raise ApiError("malformed metadata", 400, details="metadata value should be a json object")
    return metadata
