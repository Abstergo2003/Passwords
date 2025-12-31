import datetime
from dotenv import load_dotenv
import os
import jwt
import uuid
import geoip2.database
from flask_bcrypt import Bcrypt

# modules
from modules.database import connectToDatabase

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY", "wad798!@wfttu89#lol")
TOKEN_TIMEDELTA = int(os.getenv("TOKEN_TIMEDELTA", 30))
GEOIP_DB_PATH = "/geoip/GeoLite2-Country.mmdb"


def get_ip_location(ip_address: str) -> str:
    """Return geolocalization based on IP

    Args:
        ip_address (str): IP of client

    Returns:
        str: Country Name
    """
    # 1. Ignoruj sieci lokalne (Docker, LAN)
    if ip_address.startswith(("127.", "10.", "172.", "192.168.")):
        return "Local Network"

    # 2. Sprawdź czy baza istnieje
    if not os.path.exists(GEOIP_DB_PATH):
        print("ERROR: GeoIP database file not found!", flush=True)
        return "Unknown"

    try:
        # 3. Odczyt z pliku
        with geoip2.database.Reader(GEOIP_DB_PATH) as reader:
            response = reader.country(ip_address)
            country_name = response.country.name

            if country_name:
                return country_name
            return "Unknown"

    except geoip2.errors.AddressNotFoundError:  # type: ignore
        # IP nie ma w bazie (np. nowe IP lub lokalne)
        return "Unknown"
    except Exception as e:
        print(f"GeoIP Error: {e}", flush=True)
        return "Unknown"


def generate_jwt(user_id: str, remote_addr: str) -> str:
    """Generates JWT token for authorization

    Args:
        user_id (str): Clients ID in database
        remote_addr (str): Clients IP Address

    Returns:
        str: JWT token
    """
    payload = {
        "id": user_id,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(days=TOKEN_TIMEDELTA),
        "cnt": get_ip_location(remote_addr),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_jwt(token: str, remote_addr: str) -> str | None:
    """Verify's JWT token, ancd check if country of issue matches with current one

    Args:
        token (str): JWT token
        remote_addr (str): Clients IP address

    Returns:
        str | None: Clients ID in database
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if get_ip_location(remote_addr) == payload.get("cnt"):
            return payload["id"]
        else:
            return None
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def registerUser(email: str, auth_hash: str, salt: str, bcrypt: Bcrypt) -> str:
    """Registers new Client in database

    Args:
        email (str): Client's email
        auth_hash (str): Hash of clients password
        salt (str): salt
        bcrypt (Bcrypt): Bcypr object for storage security

    Returns:
        str: Client's ID in database
    """
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


def getSalt(email: str) -> str | None:
    """Returns Client's salt

    Args:
        email (str): Client's email

    Returns:
        str | None: Client's salt
    """
    [connection, cursor] = connectToDatabase()
    # Note: Use '=' for SQL comparison, not '=='
    sql_search = "SELECT encryption_salt FROM Users WHERE email = %s"
    cursor.execute(sql_search, (email,))
    result = cursor.fetchone()
    connection.close()

    if result:
        return result[0]
    return None


def loginUser(email: str, password: str, bcrypt: Bcrypt) -> tuple[bool, str | None]:
    """Logins Client

    Args:
        email (str): Client's Email
        password (str): Client's password
        bcrypt (Bcrypt): Bcrypt object to compase password hash

    Returns:
        str | None: _description_
    """
    [connection, cursor] = connectToDatabase()
    sql_serach = """
        SELECT * FROM Users WHERE email = %s
    """
    cursor.execute(sql_serach, (email,))
    users = cursor.fetchall()
    if len(users) == 0:
        return (False, None)

    user = users[0]
    connection.close()
    return (bcrypt.check_password_hash(user[2], password), user[0])


def checkEmailFree(email: str) -> bool:
    """Checks if email is Free in database

    Args:
        email (str): Future Client's email

    Returns:
        bool: Boolean value of wheter email is free
    """
    [connection, cursor] = connectToDatabase()
    sql_serach = """
        SELECT * FROM Users WHERE email = %s
    """
    cursor.execute(sql_serach, (email,))
    users = cursor.fetchall()
    connection.close()
    return len(users) == 0
