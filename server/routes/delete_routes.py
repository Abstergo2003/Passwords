from flask import Blueprint, request, make_response
from modules.authentication import (
    verify_jwt,
)
from modules.validation import (
    validate_uuid4,
)

from modules.tools import (
    generateUnauthorized,
)

from modules.crud.delete import (
    deleteCreditCard,
    deleteIdentity,
    deleteLicense,
    deletePassword,
    deleteNote,
)

delete_routes = Blueprint("delete", __name__)


@delete_routes.route("/deletePassword", methods=["DELETE"])
def deletePasswordRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    password_id = request.cookies.get("id")  # type: ignore
    is_id_valid = validate_uuid4(password_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    result = deletePassword(user_id, password_id)
    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return generateUnauthorized()


@delete_routes.route("/deleteNote", methods=["DELETE"])
def deleteNoteRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    note_id = request.cookies.get("id")  # type: ignore

    is_id_valid = validate_uuid4(note_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    result = deleteNote(user_id, note_id)
    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return generateUnauthorized()


@delete_routes.route("/deleteCreditCard", methods=["DELETE"])
def deleteCreditCardRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    card_id = request.cookies.get("id")  # type: ignore

    is_id_valid = validate_uuid4(card_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    result = deleteCreditCard(user_id, card_id)
    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return generateUnauthorized()


@delete_routes.route("/deleteIdentity", methods=["DELETE"])
def deleteIdentityRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    identity_id = request.cookies.get("id")  # type: ignore

    is_id_valid = validate_uuid4(identity_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    result = deleteIdentity(user_id, identity_id)
    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return generateUnauthorized()


@delete_routes.route("/deleteLicense", methods=["DELETE"])
def deleteLicenseRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    license_id = request.cookies.get("id")  # type: ignore

    is_id_valid = validate_uuid4(license_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    result = deleteLicense(user_id, license_id)
    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return generateUnauthorized()
