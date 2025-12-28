from flask import Blueprint, request, make_response
import json
from modules.authentication import (
    verify_jwt,
)
from modules.validation import (
    validate_uuid4,
)

from modules.tools import (
    generateUnauthorized,
)

from modules.crud.get import (
    getCreditCard,
    getIdentity,
    getLicense,
    getNote,
    getPassword,
)
from modules.database import getTeasedItems

get_routes = Blueprint("get", __name__)


@get_routes.route("/getItems", methods=["GET"])
def getItems():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id != None:
        items = getTeasedItems(user_id)
        response = make_response({"status": "ok"}, 200)
        response.set_cookie("items", json.dumps(items))
        return response
    else:
        return generateUnauthorized()


@get_routes.route("/getPassword", methods=["GET"])
def getPasswordRoute():
    token = request.cookies.get("token")
    item_id = request.cookies.get("id")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    is_id_valid = validate_uuid4(item_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    item = getPassword(user_id, item_id)
    response = make_response({"status": "ok"}, 200)
    response.set_cookie("item", json.dumps(item))
    return response


@get_routes.route("/getNote", methods=["GET"])
def getNoteRoute():
    token = request.cookies.get("token")
    item_id = request.cookies.get("id")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    is_id_valid = validate_uuid4(item_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    item = getNote(user_id, item_id)
    response = make_response({"status": "ok"}, 200)
    response.set_cookie("item", json.dumps(item))
    return response


@get_routes.route("/getCreditCard", methods=["GET"])
def getCreditCardRoute():
    token = request.cookies.get("token")
    item_id = request.cookies.get("id")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    is_id_valid = validate_uuid4(item_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    item = getCreditCard(user_id, item_id)
    response = make_response({"status": "ok"}, 200)
    response.set_cookie("item", json.dumps(item))
    return response


@get_routes.route("/getIdentity", methods=["GET"])
def getIdentityRoute():
    token = request.cookies.get("token")
    item_id = request.cookies.get("id")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    is_id_valid = validate_uuid4(item_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    item = getIdentity(user_id, item_id)
    response = make_response({"status": "ok"}, 200)
    response.set_cookie("item", json.dumps(item))
    return response


@get_routes.route("/getLicense", methods=["GET"])
def getLicenseRoute():
    token = request.cookies.get("token")
    item_id = request.cookies.get("id")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    is_id_valid = validate_uuid4(item_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    item = getLicense(user_id, item_id)
    response = make_response({"status": "ok"}, 200)
    response.set_cookie("item", json.dumps(item))
    return response
