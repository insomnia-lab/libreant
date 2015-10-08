from webant.util import routes_collector
from util import ApiError, make_success_response, on_json_load_error
from flask import request, url_for, jsonify#, current_app, jsonify
import users.api

routes = []
route = routes_collector(routes)


@route('/users/<int:userID>', methods=['GET'])
def get_user(userID):
    try:
        u = users.api.get_user(id=userID)
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return jsonify({'data': {'id': u.id, 'name': u.name}})


@route('/users/<int:userID>', methods=['DELETE'])
def delete_user(userID):
    try:
        users.api.delete_user(id=userID)
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return make_success_response("user has been successfully deleted")


@route('/users/', methods=['POST'])
def add_user():
    request.on_json_loading_failed = on_json_load_error
    userData = request.json
    if not userData:
        raise ApiError("Unsupported media type", 415)
    name = userData.get('name', None)
    if not name:
        raise ApiError("Bad Request", 400, details="missing 'name' parameter")
    password = userData.get('password', None)
    if not password:
        raise ApiError("Bad Request", 400, details="missing 'password' parameter")
    try:
        user = users.api.add_user(name=name, password=password)
    except users.api.ConflictException, e:
        raise ApiError("Conflict", 409, details=str(e))
    link_self = url_for('.get_user', userID=user.id, _external=True)
    response = jsonify({'data': {'id': user.id, 'link_self': link_self}})
    response.status_code = 201
    response.headers['Location'] = link_self
    return response


@route('/users/<int:userID>', methods=['PATCH'])
def update_user(userID):
    request.on_json_loading_failed = on_json_load_error
    if not request.json:
        raise ApiError("Unsupported media type", 415)
    try:
        users.api.update_user(userID, request.json)
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return make_success_response("user has been successfully updated")
