from flask import Blueprint, request, make_response
import requests
import string
import secrets

from modules.authentication import (
    verify_jwt,
)

from modules.tools import (
    generateUnauthorized,
)

from modules.inbucket import (
    addMailbox,
    getUserMailboxes,
    checkMailboxOwnership,
    deleteMailbox,
)


INBUCKET_API = "http://mail:9000/api/v1/mailbox"

mailbox_routes = Blueprint("mailbox", __name__)


@mailbox_routes.route("/generate-mailbox", methods=["POST"])
def generate_mailbox_route():
    token = request.cookies.get("token")
    user_id = user_id = verify_jwt(token, request.remote_addr)
    if user_id is None:
        return generateUnauthorized()

    # Tworzymy unikalną nazwę skrzynki
    suffix = "".join(
        secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8)
    )
    mailbox_name = f"pass_{suffix}"  # Prefiks 'pass' dla porządku

    if addMailbox(user_id, mailbox_name):
        return make_response(
            {"status": "ok", "email": f"{mailbox_name}@ppgroup.ddns.net"}, 201
        )
    return make_response({"error": "Database error"}, 500)


@mailbox_routes.route("/mailbox", methods=["GET"])
def list_mailboxes_route():
    token = request.cookies.get("token")
    user_id = user_id = verify_jwt(token, request.remote_addr)
    if user_id is None:
        return generateUnauthorized()

    mailboxes = getUserMailboxes(user_id)
    return make_response({"status": "ok", "mailboxes": mailboxes}, 200)


@mailbox_routes.route("/get-messages", methods=["GET"])
def get_messages_route(mailbox_name):
    token = request.cookies.get("token")
    user_id = user_id = verify_jwt(token, request.remote_addr)
    if user_id is None:
        return generateUnauthorized()

    mailbox_name = request.cookies.get("mailbox_name")

    # ZABEZPIECZENIE: Sprawdzenie własności
    if not checkMailboxOwnership(user_id, mailbox_name):
        return generateUnauthorized()

    try:
        r = requests.get(f"{INBUCKET_API}/{mailbox_name}", timeout=5)
        return make_response(r.json(), 200)
    except Exception:
        return make_response({"error": "Inbucket error"}, 500)


@mailbox_routes.route("/get-message", methods=["GET"])
def get_single_message_route():
    token = request.cookies.get("token")
    user_id = user_id = verify_jwt(token, request.remote_addr)
    if user_id is None:
        return generateUnauthorized()

    mailbox_name = request.cookies.get("mailbox_name")
    message_id = request.cookies.get("message_id")

    if not checkMailboxOwnership(user_id, mailbox_name):
        return generateUnauthorized()

    try:
        r = requests.get(f"{INBUCKET_API}/{mailbox_name}/{message_id}", timeout=5)
        return make_response(r.json(), 200)
    except Exception:
        return make_response({"error": "Inbucket error"}, 500)


@mailbox_routes.route("/delete-mailbox", methods=["DELETE"])
def delete_mailbox_api_route():
    token = request.cookies.get("token")
    user_id = user_id = verify_jwt(token, request.remote_addr)
    if user_id is None:
        return generateUnauthorized()

    mailbox_name = request.cookies.get("mailbox_name")

    if not checkMailboxOwnership(user_id, mailbox_name):
        return generateUnauthorized()

    if deleteMailbox(user_id, mailbox_name):
        return make_response({"status": "ok"}, 200)
    return make_response({"error": "Forbidden or DB error"}, 403)
