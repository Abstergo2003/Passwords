from modules.database import connectToDatabase
import uuid


def addPassword(user_id: str, data: dict) -> bool:
    [connection, cursor] = connectToDatabase()
    sql = """
    WITH new_password_entry AS (
    INSERT INTO Password (id, email, login, password, domain, tfa, favourite)
    VALUES (
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s
    )
    )
    INSERT INTO Password_User (Users_id, Password_id)
    VALUES (%s, %s)
    """
    passwordID = str(uuid.uuid4())
    cursor.execute(
        sql,
        (
            passwordID,
            data.get("email"),
            data.get("login"),
            data.get("password"),
            data.get("domain"),
            data.get("tfa"),
            False,
            user_id,
            passwordID,
        ),
    )
    connection.commit()
    connection.close()
    return True


def addNote(user_id: str, data: dict) -> bool:
    [connection, cursor] = connectToDatabase()

    sql = """
    WITH new_entry AS (
        INSERT INTO Notes (
            id, name, content, favourite
        )
        VALUES (
            %s, %s, %s, %s
        )
        RETURNING id
    )
    INSERT INTO User_Notes (Users_id, Notes_id)
    SELECT %s, id 
    FROM new_entry;
    """

    params = (
        str(uuid.uuid4()),
        data.get("name", ""),
        data.get("content", ""),
        False,
        user_id,
    )

    cursor.execute(sql, params)
    connection.commit()
    connection.close()
    return True


def addIdentity(user_id: str, data: dict) -> bool:
    [connection, cursor] = connectToDatabase()

    sql = """
    WITH new_entry AS (
        INSERT INTO "Identity" (
            id, name, surname, country, state, city, street, number, favourite
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        RETURNING id
    )
    INSERT INTO User_Identity (Users_id, Identity_id)
    SELECT %s, id 
    FROM new_entry;
    """

    params = (
        str(uuid.uuid4()),
        data.get("name", ""),
        data.get("surname", ""),
        data.get("country", ""),
        data.get("state", ""),
        data.get("city", ""),
        data.get("street", ""),
        data.get("number", ""),
        False,
        user_id,
    )

    cursor.execute(sql, params)
    connection.commit()
    connection.close()
    return True


def addCreditCard(user_id: str, data: dict) -> bool:
    [connection, cursor] = connectToDatabase()

    sql = """
    WITH new_entry AS (
        INSERT INTO CreditCard (
            id, bankName, number, brand, cvv, owner, expDate, favourite
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s
        )
        RETURNING id
    )
    INSERT INTO User_CreditCard (Users_id, CreditCard_id)
    SELECT %s, id 
    FROM new_entry;
    """

    params = (
        str(uuid.uuid4()),
        data.get("bankName", ""),
        data.get("number", ""),
        data.get("brand", ""),
        data.get("cvv", ""),
        data.get("owner", ""),
        data.get("exp_date", ""),
        False,
        user_id,
    )

    cursor.execute(sql, params)
    connection.commit()
    connection.close()
    return True


def addLicense(user_id: str, data: dict) -> bool:
    [connection, cursor] = connectToDatabase()

    sql = """
    WITH new_entry AS (
        INSERT INTO License (
            id, name, diverse, favourite
        )
        VALUES (
            %s, %s, %s, %s
        )
        RETURNING id
    )
    INSERT INTO User_License (Users_id, License_id)
    SELECT %s, id 
    FROM new_entry;
    """

    params = (
        str(uuid.uuid4()),
        data.get("name", ""),
        data.get("diverse", ""),  # This must be a JSON string or dict for the driver
        False,
        user_id,
    )

    cursor.execute(sql, params)
    connection.commit()
    connection.close()
    return True
