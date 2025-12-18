from flask import Flask, request, make_response
from flask_bcrypt import Bcrypt
import json

# import threading
import os

# ENV Variables
from dotenv import load_dotenv

# modules
from modules.authentication import (
    generate_jwt,
    verify_jwt,
    registerUser,
    loginUser,
    checkEmailFree,
    getSalt,
)
from modules.mfa import verify2fa, register2fa
from modules.crud.get import (
    getPassword,
    getNote,
    getCreditCard,
    getIdentity,
    getLicense,
)
from modules.tools import generateUnauthorized
from modules.database import getTeasedItems

from modules.crud.post import (
    addPassword,
    addNote,
    addCreditCard,
    addIdentity,
    addLicense,
)

from modules.crud.put import (
    updatePassword,
    updateNote,
    updateCreditCard,
    updateIdentity,
    updateLicense,
    switchFavourite,
)

from modules.crud.delete import (
    deletePassword,
    deleteCreditCard,
    deleteIdentity,
    deleteLicense,
    deleteNote,
)

from modules.validation import (
    password_schema,
    license_schema,
    note_schema,
    identity_schema,
    credit_card_schema,
    validate_payload,
    validate_uuid4,
    USER_EDITABLE_TABLES,
)

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY", "wad798!@wfttu89#lol")
TOKEN_TIMEDELTA = int(os.getenv("TOKEN_TIMEDELTA", 30))

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"
bcrypt = Bcrypt(app)


@app.route("/get-salt", methods=["GET"])
def get_salt_route():
    # Allow client to ask for salt by email
    email = request.args.get("email")
    if not email:
        return make_response({"error": "Email required"}, 400)

    salt = getSalt(email)
    if salt:
        return make_response({"salt": salt, "status": "ok"}, 200)
    else:
        # If user doesn't exist, we should probably return a fake salt
        # to prevent "User Enumeration" attacks, but for now:
        return make_response({"error": "User not found"}, 404)


@app.route("/register", methods=["POST"])
def register():
    # Use JSON body for data transfer
    data = request.json

    email = data.get("email")  # type: ignore
    auth_hash = data.get("auth_hash")  # type: ignore # Client sends SHA256(password)
    salt = data.get("salt")  # type: ignore # Client generates and sends this random string

    if not checkEmailFree(email):
        return make_response({"status": "Email already in use"}, 200)

    # We now store the Salt + the Auth Hash
    user_id = registerUser(email, auth_hash, salt, bcrypt)

    qr_base64 = register2fa(user_id)

    resp = make_response({"status": "ok"})
    token = generate_jwt(user_id)
    resp.set_cookie("token", token, httponly=True, samesite="Lax")
    resp.set_cookie("qr_code", qr_base64)
    return resp


@app.route("/login", methods=["POST"])
def login_route():
    # Use JSON body
    data = request.json
    email = data.get("email")  # type: ignore
    auth_hash = data.get("auth_hash")  # type: ignore # Client sends SHA256(password)
    code = data.get("code")  # type: ignore

    # loginUser verifies Bcrypt(auth_hash) matches DB
    [result, user_id] = loginUser(email, auth_hash, bcrypt)
    ver_result = verify2fa(user_id, code)

    if result and ver_result:
        token = generate_jwt(user_id)
        response = make_response({"status": "ok"}, 200)
        response.set_cookie("token", token, httponly=True, samesite="Lax")
        return response
    else:
        return generateUnauthorized()


@app.route("/getItems", methods=["GET"])
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


@app.route("/addPassword", methods=["POST"])
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
    result = addPassword(
        user_id,
        data["email"],  # type: ignore
        data["login"],  # type: ignore
        data["password"],  # type: ignore
        data["domain"],  # type: ignore
        data["tfa"],  # type: ignore
        data.get("favourite", False),  # Default to False if missing # type: ignore
    )

    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return make_response({"error": "Database error"}, 500)


@app.route("/addNote", methods=["POST"])
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
    result = addNote(
        user_id, data["name"], data["content"], data.get("favourite", False)  # type: ignore
    )

    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return make_response({"error": "Database error"}, 500)


@app.route("/addCreditCard", methods=["POST"])
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


@app.route("/addIdentity", methods=["POST"])
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
        data.get("favourite", False),  # type: ignore
    )

    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return make_response({"error": "Database error"}, 500)


@app.route("/addLicense", methods=["POST"])
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
    result = addLicense(
        user_id, data["name"], data["diverse"], data.get("favourite", False)  # type: ignore
    )

    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return make_response({"error": "Database error"}, 500)


@app.route("/updatePassword", methods=["PUT"])
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


@app.route("/updateNote", methods=["PUT"])
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


@app.route("/updateCreditCard", methods=["PUT"])
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


@app.route("/updateIdentity", methods=["PUT"])
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


@app.route("/updateLicense", methods=["PUT"])
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


@app.route("/favourite", methods=["PUT"])
def setFavouriteRoute():
    token = request.cookies.get("token")
    user_id = verify_jwt(token)
    if user_id is None:
        return generateUnauthorized()

    item_id = request.cookies.get("id")
    is_id_valid = validate_uuid4(item_id)
    if not is_id_valid:
        return make_response({"error": "invalid id"}, 400)

    category = request.cookies.get("category")

    if category not in USER_EDITABLE_TABLES:
        return generateUnauthorized()

    result = switchFavourite(user_id, item_id, category)

    if result:
        return make_response({"status": "ok"}, 200)
    else:
        return generateUnauthorized()


@app.route("/getPassword", methods=["GET"])
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


@app.route("/getNote", methods=["GET"])
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


@app.route("/getCreditCard", methods=["GET"])
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


@app.route("/getIdentity", methods=["GET"])
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


@app.route("/getLicense", methods=["GET"])
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


@app.route("/deletePassword", methods=["DELETE"])
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


@app.route("/deleteNote", methods=["DELETE"])
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


@app.route("/deleteCreditCard", methods=["DELETE"])
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


@app.route("/deleteIdentity", methods=["DELETE"])
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


@app.route("/deleteLicense", methods=["DELETE"])
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


if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0", threaded=True)
