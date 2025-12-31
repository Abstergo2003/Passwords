import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()


DATABASE_DATABASE = os.getenv("DATABASE_DATABASE")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")


def connectToDatabase():
    """Creates Connection to database

    Returns:
        list: [connection, cursor]
    """
    connection = psycopg2.connect(
        database=DATABASE_DATABASE,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
    )

    cursor = connection.cursor()
    return [connection, cursor]


def getTeasedPasswords(user_id: str) -> list:
    """Returns partial data from Passwords table

    Args:
        user_id (str): Client's id in database

    Returns:
        list: list of dict with (id, login, domain)
    """
    [connection, cursor] = connectToDatabase()
    sql = """
        SELECT p.id, p.login, p.domain, FROM Password p JOIN  Password_User pu ON p.id = pu.Password_id WHERE pu.Users_id = %s;
    """
    cursor.execute(sql, (user_id,))
    items = cursor.fetchall()
    connection.close()
    teased = []
    for password in items:
        teased.append(
            {
                "spanU": password[2],
                "spanD": password[1],
                "id": password[0],
            }
        )
    return teased


def getTeasedNotes(user_id: str) -> list:
    """Returns partial data from Notes table

    Args:
        user_id (str): Client's id in database

    Returns:
        list: list of dict with (id, name, content)
    """
    [connection, cursor] = connectToDatabase()
    sql = """
        SELECT p.id, p.name, p.content FROM Notes p JOIN  User_Notes pu ON p.id = pu.Notes_id WHERE pu.Users_id = %s;
    """
    cursor.execute(sql, (user_id,))
    items = cursor.fetchall()
    connection.close()
    teased = []
    for password in items:
        teased.append(
            {
                "spanU": password[1],
                "spanD": "",
                "id": password[0],
            }
        )
    return teased


def getTeasedLicenses(user_id: str) -> list:
    """Returns partial data from License table

    Args:
        user_id (str): Client's id in database

    Returns:
        list: list of dict with (id, name)
    """
    [connection, cursor] = connectToDatabase()
    sql = """
        SELECT p.id, p.name FROM License p JOIN  User_License pu ON p.id = pu.License_id WHERE pu.Users_id = %s;
    """
    cursor.execute(sql, (user_id,))
    items = cursor.fetchall()
    connection.close()
    teased = []
    for password in items:
        teased.append(
            {
                "spanU": password[1],
                "spanD": "",
                "id": password[0],
            }
        )
    return teased


def getTeasedIdentity(user_id: str) -> list:
    """Returns partial data from Identity table

    Args:
        user_id (str): Client's id in database

    Returns:
        list: list of dict with (id, name, surname)
    """
    [connection, cursor] = connectToDatabase()
    sql = """
        SELECT p.id, p.name, p.surname FROM "Identity" p JOIN User_Identity pu ON p.id = pu.Identity_id WHERE pu.Users_id = %s;
    """
    cursor.execute(sql, (user_id,))
    items = cursor.fetchall()
    connection.close()
    teased = []
    for password in items:
        teased.append(
            {
                "spanU": f"{password[1]} {password[2]}",
                "spanD": password[3],
                "id": password[0],
            }
        )
    return teased


def getTeasedCreditCard(user_id: str) -> list:
    """Returns partial data from CreditCard table

    Args:
        user_id (str): Client's id in database

    Returns:
        list: list of dict with (id, bankName, number)
    """
    [connection, cursor] = connectToDatabase()
    sql = """
        SELECT p.id, p.bankName, p.number FROM CreditCard p JOIN  User_CreditCard pu ON p.id = pu.CreditCard_id WHERE pu.Users_id = %s;
    """
    cursor.execute(sql, (user_id,))
    items = cursor.fetchall()
    connection.close()
    teased = []
    for password in items:
        teased.append(
            {
                "spanU": password[1],
                "spanD": password[2],
                "id": password[0],
            }
        )
    return teased


def getTeasedItems(user_id: str) -> dict:
    """Return combined data from all getTeased... functions as dict

    Args:
        user_id (str): Client's id in database

    Returns:
        dict: dict with lists at aliases (passwords, notes, licenses, identities, creditCards)
    """
    passwords = getTeasedPasswords(user_id)
    notes = getTeasedNotes(user_id)
    licenses = getTeasedLicenses(user_id)
    identities = getTeasedIdentity(user_id)
    creditCards = getTeasedCreditCard(user_id)
    return {
        "passwords": passwords,
        "notes": notes,
        "licenses": licenses,
        "identities": identities,
        "creditCards": creditCards,
    }
