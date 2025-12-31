import pyotp
import qrcode
from io import BytesIO
import base64

# modules
from modules.database import connectToDatabase


def generate_2fa_qrcode(email: str) -> list[str]:
    """Generates qr code for 2fa

    Args:
        email (str): Client's email in database

    Returns:
        list[str]: [key, qr_base64]
    """
    key = pyotp.random_base32()
    uri = pyotp.totp.TOTP(key).provisioning_uri(
        name=email, issuer_name="Passwords## by Abstergo##"
    )
    img = qrcode.make(uri)
    buffer = BytesIO()
    img.save(buffer)
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return [key, qr_base64]


def verify2fa(id: str, code: str) -> bool:
    """Verifies provided 2fa code

    Args:
        id (str): Client's ID in database
        code (str): 2fa code

    Returns:
        bool: Result of verification
    """

    [connection, cursor] = connectToDatabase()
    sql_serach = """
        SELECT * FROM Users WHERE id = %s
    """
    cursor.execute(sql_serach, (id,))
    users = cursor.fetchall()
    if len(users) == 0:
        return False

    user = users[0]
    totp = pyotp.TOTP(user[3])
    connection.close()
    return totp.verify(code)


def register2fa(id: str) -> str:
    """Registers 2fa for Client in database

    Args:
        id (str): Client's ID in database

    Returns:
        str: base64 of qr code for 2fa
    """
    [connection, cursor] = connectToDatabase()
    sql_serach = """
        SELECT * FROM Users WHERE id = %s
    """
    cursor.execute(sql_serach, (id,))
    users = cursor.fetchall()
    if len(users) == 0:
        return ""

    user = users[0]
    email = user[1]
    [key, qr_base64] = generate_2fa_qrcode(email)
    sql_update = """
        UPDATE Users SET tfaCode = %s WHERE id = %s
    """
    cursor.execute(sql_update, (key, id))
    connection.commit()
    connection.close()
    return qr_base64
