from flask import Blueprint, request, make_response
from modules.authentication import verify_jwt
from modules.validation import (
    validate_uuid4,
    validate_payload,
    password_schema,
    credit_card_schema,
    note_schema,
    license_schema,
    identity_schema,
)
from modules.tools import (
    generateUnauthorized,
)
from modules.crud.put import (
    updateCreditCard,
    updateIdentity,
    updateLicense,
    updateNote,
    updatePassword,
)

update_routes = Blueprint("update", __name__)


@update_routes.route("/updatePassword", methods=["PUT"])
def updatePasswordRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    data = request.json

    is_valid, error_msg = validate_payload(data, password_schema)

    if not is_valid:
        return make_response({"error": error_msg}, 400)

    password_id = request.cookies.get("id")  # type: ignore

    is_id_valid = validate_uuid4(password_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    password_data = {
        "email": data.get("email"),  # type: ignore
        "login": data.get("login"),  # type: ignore
        "password": data.get("password"),  # type: ignore
        "domain": data.get("domain"),  # type: ignore
        "tfa": data.get("tfa"),  # type: ignore
    }
    result = updatePassword(user_id, password_id, password_data)
    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return generateUnauthorized()


@update_routes.route("/updateNote", methods=["PUT"])
def updateNoteRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    data = request.json

    is_valid, error_msg = validate_payload(data, note_schema)
    if not is_valid:
        return make_response({"error": error_msg}, 400)

    note_id = request.cookies.get("id")
    is_id_valid = validate_uuid4(note_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    result = updateNote(user_id, note_id, data.get("name"), data.get("content"))  # type: ignore
    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return generateUnauthorized()


@update_routes.route("/updateCreditCard", methods=["PUT"])
def updateCreditCardRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    data = request.json

    is_valid, error_msg = validate_payload(data, credit_card_schema)

    if not is_valid:
        return make_response({"error": error_msg}, 400)

    card_id = request.cookies.get("id")
    is_id_valid = validate_uuid4(card_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    result = updateCreditCard(
        user_id,
        card_id,
        data.get("bankName"),  # type: ignore
        data.get("number"),  # type: ignore
        data.get("brand"),  # type: ignore
        data.get("cvv"),  # type: ignore
        data.get("owner"),  # type: ignore
        data.get("exp_date"),  # type: ignore
    )
    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return generateUnauthorized()


@update_routes.route("/updateIdentity", methods=["PUT"])
def updateIdentityRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    data = request.json

    is_valid, error_msg = validate_payload(data, identity_schema)

    if not is_valid:
        return make_response({"error": error_msg}, 400)

    identity_id = request.cookies.get("id")
    is_id_valid = validate_uuid4(identity_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    result = updateIdentity(
        user_id,
        identity_id,
        data.get("name"),  # type: ignore
        data.get("surname"),  # type: ignore
        data.get("country"),  # type: ignore
        data.get("state"),  # type: ignore
        data.get("city"),  # type: ignore
        data.get("street"),  # type: ignore
        data.get("number"),  # type: ignore
    )
    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return generateUnauthorized()


@update_routes.route("/updateLicense", methods=["PUT"])
def updateLicenseRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    data = request.json

    is_valid, error_msg = validate_payload(data, license_schema)

    if not is_valid:
        return make_response({"error": error_msg}, 400)

    license_id = request.cookies.get("id")
    is_id_valid = validate_uuid4(license_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    result = updateLicense(
        user_id,
        license_id,
        data.get("name"),  # type: ignore
        data.get("diverse"),  # type: ignore
    )
    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return generateUnauthorized()
