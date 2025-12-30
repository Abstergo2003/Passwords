from flask import Blueprint, request, make_response
from modules.tools import bcrypt
import os

from dotenv import load_dotenv


from modules.authentication import (
    getSalt,
    generate_jwt,
    registerUser,
    loginUser,
    checkEmailFree,
)

from modules.mfa import register2fa, verify2fa

from modules.tools import (
    generateUnauthorized,
)

load_dotenv()

ALLOW_REGISTER = os.getenv("ALLOW_REGISTER", "1")

authenticate_routes = Blueprint("authenticate", __name__)


@authenticate_routes.route("/get-salt", methods=["GET"])
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


if ALLOW_REGISTER == "1":

    @authenticate_routes.route("/register", methods=["POST"])
    def register():

        if ALLOW_REGISTER == "0":
            return make_response({"status": "Register not allowed"}, 403)

        data = request.json

        email = data.get("email")
        auth_hash = data.get("auth_hash")  # Client sends SHA256(password)
        salt = data.get("salt")  # Client generates and sends this random string

        if not checkEmailFree(email):
            return make_response({"status": "Email already in use"}, 200)

        user_id = registerUser(email, auth_hash, salt, bcrypt)

        qr_base64 = register2fa(user_id)

        resp = make_response({"status": "ok"})
        token = generate_jwt(user_id, request.remote_addr or "")
        resp.set_cookie("token", token, httponly=True, samesite="Lax")
        resp.set_cookie("qr_code", qr_base64)
        return resp


@authenticate_routes.route("/login", methods=["POST"])
def login_route():
    # Use JSON body
    data = request.json
    email = data.get("email")
    auth_hash = data.get("auth_hash")  # Client sends SHA256(password)
    code = data.get("code")

    # loginUser verifies Bcrypt(auth_hash) matches DB
    [result, user_id] = loginUser(email, auth_hash, bcrypt)
    ver_result = verify2fa(user_id or "", code)
    if result and ver_result:
        token = generate_jwt(user_id or "", request.remote_addr or "")
        response = make_response({"status": "ok"}, 200)
        response.set_cookie("token", token, httponly=True, samesite="Lax")
        return response
    else:
        return generateUnauthorized()
