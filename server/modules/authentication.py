import datetime
from dotenv import load_dotenv
import os
import jwt
import uuid


# modules
from modules.database import connectToDatabase

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY", "wad798!@wfttu89#lol")
TOKEN_TIMEDELTA = int(os.getenv("TOKEN_TIMEDELTA", 30))


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


def registerUser(email, auth_hash, salt, bcrypt):
    [connection, cursor] = connectToDatabase()
    user_id = str(uuid.uuid4())

    # We hash the "Auth Hash" again with Bcrypt for storage security
    # effectively: Bcrypt(SHA256(real_password))
    final_hash = bcrypt.generate_password_hash(auth_hash).decode("utf-8")

    sql_context = """
        INSERT INTO Users (id, email, passwordHash, salt, tfaCode) 
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql_context, (user_id, email, final_hash, salt, ""))
    connection.commit()
    connection.close()
    return user_id


def getSalt(email):
    [connection, cursor] = connectToDatabase()
    # Note: Use '=' for SQL comparison, not '=='
    sql_search = "SELECT encryption_salt FROM Users WHERE email = %s"
    cursor.execute(sql_search, (email,))
    result = cursor.fetchone()
    connection.close()

    if result:
        return result[0]
    return None


def loginUser(email, password, bcrypt):
    [connection, cursor] = connectToDatabase()
    sql_serach = """
        SELECT * FROM Users WHERE email = %s
    """
    cursor.execute(sql_serach, (email,))
    user = cursor.fetchall()[0]
    connection.close()
    return [bcrypt.check_password_hash(user[2], password), user[0]]


def checkEmailFree(email):
    [connection, cursor] = connectToDatabase()
    sql_serach = """
        SELECT * FROM Users WHERE email = %s
    """
    cursor.execute(sql_serach, (email,))
    users = cursor.fetchall()
    connection.close()
    return len(users) == 0
