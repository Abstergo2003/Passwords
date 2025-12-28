from flask import Blueprint, request, make_response
from modules.authentication import (
    verify_jwt,
)
from modules.validation import (
    validate_payload,
    password_schema,
    note_schema,
    credit_card_schema,
    license_schema,
    identity_schema,
)

from modules.tools import (
    generateUnauthorized,
)

from modules.crud.post import (
    addCreditCard,
    addIdentity,
    addLicense,
    addNote,
    addPassword,
)

add_routes = Blueprint("add", __name__)


@add_routes.route("/addPassword", methods=["POST"])
def addPasswordRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    data = request.json

    is_valid, error_msg = validate_payload(data, password_schema)

    if not is_valid:
        return make_response({"error": error_msg}, 400)

    # 2. Execute
    # Fixed typo: 'addPasssword' -> 'addPassword'
    result = addPassword(user_id, data)  # Default to False if missing # type: ignore

    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return make_response({"error": "Database error"}, 500)


@add_routes.route("/addNote", methods=["POST"])
def addNoteRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    data = request.json

    # 1. Validate
    is_valid, error_msg = validate_payload(data, note_schema)
    if not is_valid:
        return make_response({"error": error_msg}, 400)

    # 2. Execute
    result = addNote(user_id, data["name"], data["content"])  # type: ignore

    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return make_response({"error": "Database error"}, 500)


@add_routes.route("/addCreditCard", methods=["POST"])
def addCreditCardRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    data = request.json

    is_valid, error_msg = validate_payload(data, credit_card_schema)

    if not is_valid:
        return make_response({"error": error_msg}, 400)

    # 2. Execute
    result = addCreditCard(
        user_id,
        data["bankName"],  # type: ignore
        data["number"],  # type: ignore
        data["brand"],  # type: ignore
        data["cvv"],  # type: ignore
        data["owner"],  # type: ignore
        data["exp_date"],  # type: ignore
        data.get("favourite", False),  # type: ignore
    )

    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return make_response({"error": "Database error"}, 500)


@add_routes.route("/addIdentity", methods=["POST"])
def addIdentityRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    data = request.json

    is_valid, error_msg = validate_payload(data, identity_schema)

    if not is_valid:
        return make_response({"error": error_msg}, 400)

    # 2. Execute
    result = addIdentity(
        user_id,
        data["name"],  # type: ignore
        data["surname"],  # type: ignore
        data["country"],  # type: ignore
        data["state"],  # type: ignore
        data["city"],  # type: ignore
        data["street"],  # type: ignore
        data["number"],  # type: ignore
    )

    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return make_response({"error": "Database error"}, 500)


@add_routes.route("/addLicense", methods=["POST"])
def addLicenseRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    data = request.json

    # 1. Validate
    # 'diverse' should be a JSON object or string, validation just checks presence here
    is_valid, error_msg = validate_payload(data, license_schema)

    if not is_valid:
        return make_response({"error": error_msg}, 400)

    # 2. Execute
    result = addLicense(user_id, data["name"], data["diverse"])  # type: ignore

    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return make_response({"error": "Database error"}, 500)
