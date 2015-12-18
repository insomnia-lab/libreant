from webant.util import routes_collector
from util import ApiError, make_success_response, on_json_load_error
from flask import request, url_for, jsonify#, current_app, jsonify
import users.api
from users import Action, Capability

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


@route('/groups/<int:groupID>', methods=['GET'])
def get_group(groupID):
    try:
        g = users.api.get_group(id=groupID)
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return jsonify({'data': {'id': g.id, 'name': g.name}})


@route('/groups/<int:groupID>', methods=['DELETE'])
def delete_group(groupID):
    try:
        users.api.delete_group(id=groupID)
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return make_success_response("group has been successfully deleted")


@route('/groups/', methods=['POST'])
def add_group():
    request.on_json_loading_failed = on_json_load_error
    groupData = request.json
    if not groupData:
        raise ApiError("Unsupported media type", 415)
    name = groupData.get('name', None)
    if not name:
        raise ApiError("Bad Request", 400, details="missing 'name' parameter")
    try:
        group = users.api.add_group(name=name)
    except users.api.ConflictException, e:
        raise ApiError("Conflict", 409, details=str(e))
    link_self = url_for('.get_group', groupID=group.id, _external=True)
    response = jsonify({'data': {'id': group.id, 'link_self': link_self}})
    response.status_code = 201
    response.headers['Location'] = link_self
    return response


@route('/groups/<int:groupID>', methods=['PATCH'])
def update_group(groupID):
    request.on_json_loading_failed = on_json_load_error
    if not request.json:
        raise ApiError("Unsupported media type", 415)
    try:
        users.api.update_group(groupID, request.json)
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return make_success_response("group has been successfully updated")


@route('/groups/<int:groupID>/users/<int:userID>', methods=['PUT'])
def add_user_to_group(groupID, userID):
    try:
        users.api.add_user_to_group(userID, groupID)
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return make_success_response("user has been successfully added to group")


@route('/groups/<int:groupID>/users/<int:userID>', methods=['DELETE'])
def delete_user_from_group(groupID, userID):
    try:
        users.api.remove_user_from_group(userID, groupID)
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return make_success_response("user has been successfully removed from group")


@route('/groups/<int:groupID>/users/', methods=['GET'])
def get_users_in_group(groupID):
    try:
        us = [{'id': u.id} for u in users.api.get_users_in_group(groupID)]
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return jsonify({'data': us})


@route('/users/<int:userID>/groups/', methods=['GET'])
def get_groups_of_user(userID):
    try:
        groups = [{'id': g.id} for g in users.api.get_groups_of_user(userID)]
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return jsonify({'data': groups})


@route('/capabilities/<int:capID>', methods=['GET'])
def get_capability(capID):
    try:
        cap = users.api.get_capability(capID)
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return jsonify({'data':
                      {'id': cap.id,
                       'domain': Capability.regToSim(cap.domain),
                       'actions': cap.action.to_list()}})


@route('/capabilities/<int:capID>', methods=['DELETE'])
def delete_capability(capID):
    try:
        users.api.delete_capability(capID)
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return make_success_response("capability has been successfully deleted")


@route('/capabilities/', methods=['POST'])
def add_capability():
    request.on_json_loading_failed = on_json_load_error
    capData = request.json
    if not capData:
        raise ApiError("Unsupported media type", 415)
    domain = capData.get('domain', None)
    if not domain:
        raise ApiError("Bad Request", 400, details="missing 'domain' parameter")
    actions = capData.get('actions', None)
    if not actions:
        raise ApiError("Bad Request", 400, details="missing 'actions' parameter")
    try:
        cap = users.api.add_capability(domain=domain, action=Action.from_list(actions))
    except users.api.ConflictException, e:
        raise ApiError("Conflict", 409, details=str(e))
    link_self = url_for('.get_capability', capID=cap.id, _external=True)
    response = jsonify({'data': {'id': cap.id, 'link_self': link_self}})
    response.status_code = 201
    response.headers['Location'] = link_self
    return response


@route('/capabilities/<int:capID>', methods=['PATCH'])
def update_capability(capID):
    request.on_json_loading_failed = on_json_load_error
    if not request.json:
        raise ApiError("Unsupported media type", 415)
    updates = request.json
    if 'actions' in updates:
        updates['action'] = Action.from_list(updates.pop('actions'))
    try:
        users.api.update_capability(capID, updates)
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return make_success_response("capability has been successfully updated")


@route('/groups/<int:groupID>/capabilities/<int:capID>', methods=['PUT'])
def add_capability_to_group(groupID, capID):
    try:
        users.api.add_capability_to_group(capID, groupID)
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return make_success_response("capability has been successfully added to group")


@route('/groups/<int:groupID>/capabilities/<int:capID>', methods=['DELETE'])
def delete_capability_from_group(groupID, capID):
    try:
        users.api.remove_capability_from_group(capID, groupID)
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return make_success_response("capability has been successfully removed from group")


@route('/groups/<int:groupID>/capabilities/', methods=['GET'])
def get_capabilities_of_group(groupID):
    try:
        caps = [{'id': cap.id} for cap in users.api.get_capabilities_of_group(groupID)]
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return jsonify({'data': caps})


@route('/capabilities/<int:capID>/groups/', methods=['GET'])
def get_groups_with_capability(capID):
    try:
        groups = [{'id': g.id} for g in users.api.get_groups_with_capability(capID)]
    except users.api.NotFoundException, e:
        raise ApiError("Not found", 404, details=str(e))
    return jsonify({'data': groups})
