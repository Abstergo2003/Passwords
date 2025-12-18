from modules.database import connectToDatabase


def deletePassword(user_id, password_id):
    [connection, cursor] = connectToDatabase()
    sql = """
    WITH deleted_relationship AS (
    DELETE FROM Password_User
    WHERE Users_id = %s 
        AND Password_id = %s
    RETURNING Password_id
    )
    DELETE FROM Password
    WHERE id IN (SELECT Password_id FROM deleted_relationship);
    """
    cursor.execute(
        sql,
        (user_id, password_id),
    )
    connection.commit()
    connection.close()
    return True


def deleteNote(user_id, note_id):
    [connection, cursor] = connectToDatabase()

    sql = """
    WITH deleted_relationship AS (
        DELETE FROM User_Notes
        WHERE Users_id = %s 
          AND Notes_id = %s
        RETURNING Notes_id
    )
    DELETE FROM Notes
    WHERE id IN (SELECT Notes_id FROM deleted_relationship);
    """

    cursor.execute(sql, (user_id, note_id))
    connection.commit()
    connection.close()
    return True


def deleteIdentity(user_id, identity_id):
    [connection, cursor] = connectToDatabase()

    sql = """
    WITH deleted_relationship AS (
        DELETE FROM User_Identity
        WHERE Users_id = %s 
          AND Identity_id = %s
        RETURNING Identity_id
    )
    DELETE FROM "Identity"
    WHERE id IN (SELECT Identity_id FROM deleted_relationship);
    """

    cursor.execute(sql, (user_id, identity_id))
    connection.commit()
    connection.close()
    return True


def deleteCreditCard(user_id, card_id):
    [connection, cursor] = connectToDatabase()

    sql = """
    WITH deleted_relationship AS (
        DELETE FROM User_CreditCard
        WHERE Users_id = %s 
          AND CreditCard_id = %s
        RETURNING CreditCard_id
    )
    DELETE FROM CreditCard
    WHERE id IN (SELECT CreditCard_id FROM deleted_relationship);
    """

    cursor.execute(sql, (user_id, card_id))
    connection.commit()
    connection.close()
    return True


def deleteLicense(user_id, license_id):
    [connection, cursor] = connectToDatabase()

    sql = """
    WITH deleted_relationship AS (
        DELETE FROM User_License
        WHERE Users_id = %s 
          AND License_id = %s
        RETURNING License_id
    )
    DELETE FROM License
    WHERE id IN (SELECT License_id FROM deleted_relationship);
    """

    cursor.execute(sql, (user_id, license_id))
    connection.commit()
    connection.close()
    return True
