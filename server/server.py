from flask import Flask, request, make_response, send_file
from flask_bcrypt import Bcrypt
import json
import time
import psycopg2
import uuid


# import threading
import os
import jwt
from jwt.exceptions import DecodeError
import datetime

# 2fa
import pyotp
import qrcode
from io import BytesIO
import base64
from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY", "wad798!@wfttu89#lol")
TOKEN_TIMEDELTA = int(os.getenv("TOKEN_TIMEDELTA", 30))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"
bcrypt = Bcrypt(app)


def connectToDatabase():
    connection = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="docker",
        host="localhost",
        port=5432,
    )

    cursor = connection.cursor()
    return [connection, cursor]


def generate_jwt(user_id):
    payload = {
        "id": user_id,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(days=TOKEN_TIMEDELTA),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["id"]
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def verify2fa(id, code):
    [connection, cursor] = connectToDatabase()
    sql_serach = f"""
        SELECT * FROM Users WHERE id == {id}
    """
    cursor.execute(sql_serach)
    user = cursor.fetchall()[0]
    totp = pyotp.TOTP(user[3])
    connection.close()
    return totp.verify(code)


def generate_2fa_qrcode(id):
    [connection, cursor] = connectToDatabase()
    sql_serach = f"""
        SELECT * FROM Users WHERE id == {id}
    """
    cursor.execute(sql_serach)
    user = cursor.fetchall()[0]
    email = user[1]
    connection.close()
    key = pyotp.random_base32()
    uri = pyotp.totp.TOTP(key).provisioning_uri(
        name=email, issuer_name="Passwords## by Abstergo##"
    )
    img = qrcode.make(uri)
    buffer = BytesIO()
    img.save(buffer)
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return [key, qr_base64]


def registerUser(email, password):
    [connection, cursor] = connectToDatabase()
    user_id = str(uuid.uuid4())
    password_hash = bcrypt.generate_password_hash(password)
    sql_context = """
        INSERT INTO Users (id, email, passwordHash, tfaCode) VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql_context, (user_id, email, password_hash, ""))
    connection.commit()
    connection.close()
    return user_id


def register2fa(id):
    [connection, cursor] = connectToDatabase()
    sql_serach = """
        SELECT * FROM Users WHERE id == %s
    """
    cursor.execute(sql_serach, (id))
    user = cursor.fetchall()[0]
    email = user[1]
    [key, qr_base64] = generate_2fa_qrcode(email)
    sql_update = """
        UPDATE Users SET tfaCode = %s WHERE id = %s
    """
    cursor.execute(sql_update, (key, id))
    connection.commit()
    connection.close()
    return qr_base64


def loginUser(email, password):
    [connection, cursor] = connectToDatabase()
    sql_serach = """
        SELECT * FROM Users WHERE email == %s
    """
    cursor.execute(sql_serach, (email))
    user = cursor.fetchall()[0]
    connection.close()
    return [bcrypt.check_password_hash(user[2], password), user[0]]


def checkEmailFree(email):
    [connection, cursor] = connectToDatabase()
    sql_serach = """
        SELECT * FROM Users WHERE email == %s
    """
    cursor.execute(sql_serach, (email))
    users = cursor.fetchall()
    connection.close()
    return len(users) == 0


@app.route("/register", methods=["POST"])
def register():
    email = request.cookies.get("email")
    password = request.cookies.get("password")
    if not checkEmailFree(email):
        return make_response({"status": "Email already in use"}, 200)
    user_id = registerUser(email, password)
    qr_base64 = register2fa(user_id)
    resp = make_response({"status": "ok"})
    token = jwt.encode({"id": user_id}, SECRET_KEY, algorithm="HS256")
    resp.set_cookie("token", token, httponly=True, samesite="Lax")
    resp.set_cookie("qr_code", qr_base64)
    return resp


@app.route("/login", methods=["POST"])
def login_route():
    email = request.cookies.get("email")
    password = request.cookies.get("password")
    code = request.cookies.get("code")
    [result, user_id] = loginUser(email, password)
    ver_result = verify2fa(user_id, code)
    if result and ver_result:
        token = generate_jwt(user_id)
        response = make_response(
            {"status": "ok"},
            200,
        )
        response.set_cookie("token", token)
        return response
    else:
        response = make_response(
            {"error": "Unauthorized"},
            401,
        )
        return response


if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0", threaded=True)
