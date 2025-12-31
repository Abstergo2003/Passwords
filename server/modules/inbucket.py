import uuid
import requests
from modules.database import connectToDatabase

# Konfiguracja Inbucketa (nazwa serwisu w sieci Docker)
INBUCKET_API = "http://mail:9000/api/v1/mailbox"


def addMailbox(user_id: str, mailbox_name: str) -> bool:
    """Saves new mailbox assigned to Client

    Args:
        user_id (str): Client's ID in database
        mailbox_name (str): Alias of mailbox ex test@test.com

    Returns:
        bool: Result of operation
    """
    [connection, cursor] = connectToDatabase()
    mailbox_id = str(uuid.uuid4())
    sql = "INSERT INTO Users_mail (id, Users_id, mail) VALUES (%s, %s, %s);"
    try:
        cursor.execute(sql, (mailbox_id, user_id, mailbox_name))
        connection.commit()
        return True
    except Exception as e:
        print(f"DB Error (addMailbox): {e}")
        return False
    finally:
        connection.close()


def getUserMailboxes(user_id: str) -> list:
    """Gets mailboxes assigned to Client

    Args:
        user_id (str): Client's ID in database

    Returns:
        list: list of Client assigned mailboxes
    """
    [connection, cursor] = connectToDatabase()
    sql = "SELECT mail FROM Users_mail WHERE Users_id = %s;"
    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()
    connection.close()
    return [row[0] for row in rows]


def checkMailboxOwnership(user_id: str, mailbox_name: str) -> bool:
    """Checks whether mailbox is assigned to Client

    Args:
        user_id (str): Client's ID in database
        mailbox_name (str): Alias of mailbox

    Returns:
        bool: Result of being assigned to Client
    """
    [connection, cursor] = connectToDatabase()
    sql = "SELECT 1 FROM Users_mail WHERE Users_id = %s AND mail = %s;"
    cursor.execute(sql, (user_id, mailbox_name))
    exists = cursor.fetchone() is not None
    connection.close()
    return exists


def deleteMailbox(user_id: str, mailbox_name: str) -> bool:
    """Delete's mailbox from database and clears mails

    Args:
        user_id (str): Client's ID in database
        mailbox_name (str): Alias of mailbox

    Returns:
        bool: Result of deletion operation
    """
    [connection, cursor] = connectToDatabase()
    sql = "DELETE FROM Users_mail WHERE Users_id = %s AND mail = %s;"
    try:
        cursor.execute(sql, (user_id, mailbox_name))
        if cursor.rowcount > 0:
            connection.commit()
            # Fizyczne usunięcie maili z Inbucketa
            requests.delete(f"{INBUCKET_API}/{mailbox_name}", timeout=5)
            return True
        return False
    except Exception as e:
        print(f"Error (deleteMailbox): {e}")
        return False
    finally:
        connection.close()
