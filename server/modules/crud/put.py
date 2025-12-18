from modules.database import connectToDatabase


def updatePassword(user_id, password_id, data):
    [connection, cursor] = connectToDatabase()
    sql = """
    UPDATE Password
    SET
        login = %s,
        password = %s, 
        email = %s,
        domain = %s,
        tfa = %s
    WHERE
        id = %s
        AND id IN (
            SELECT Password_id
            FROM Password_User
            WHERE Users_id = %s
        );
    """
    cursor.execute(
        sql,
        (
            data.get("login"),
            data.get("password"),
            data.get("email"),
            data.get("domain"),
            data.get("tfa"),
            password_id,
            user_id,
        ),
    )
    connection.commit()
    connection.close()
    return True


def updateNote(user_id, note_id, name, content):
    [connection, cursor] = connectToDatabase()

    sql = """
    UPDATE Notes
    SET 
        name = %s,
        content = %s
    WHERE 
        id = %s
        AND id IN (
            SELECT Notes_id 
            FROM User_Notes 
            WHERE Users_id = %s
        );
    """

    params = (name, content, note_id, user_id)

    cursor.execute(sql, params)
    connection.commit()
    connection.close()
    return True


def updateIdentity(
    user_id,
    identity_id,
    name,
    surname,
    country,
    state,
    city,
    street,
    number,
):
    [connection, cursor] = connectToDatabase()

    sql = """
    UPDATE "Identity"
    SET 
        name = %s,
        surname = %s,
        IDnumber = %s,
        country = %s,
        state = %s,
        city = %s,
        street = %s,
        number = %s
    WHERE 
        id = %s
        AND id IN (
            SELECT Identity_id 
            FROM User_Identity 
            WHERE Users_id = %s
        );
    """

    params = (
        name,
        surname,
        country,
        state,
        city,
        street,
        number,
        identity_id,
        user_id,
    )

    cursor.execute(sql, params)
    connection.commit()
    connection.close()
    return True


def updateCreditCard(user_id, card_id, bank_name, number, brand, cvv, owner, exp_date):
    [connection, cursor] = connectToDatabase()

    sql = """
    UPDATE CreditCard
    SET 
        bankName = %s,
        number = %s,
        brand = %s,
        cvv = %s,
        owner = %s,
        expDate = %s
    WHERE 
        id = %s
        AND id IN (
            SELECT CreditCard_id 
            FROM User_CreditCard 
            WHERE Users_id = %s
        );
    """

    params = (
        bank_name,
        number,
        brand,
        cvv,
        owner,
        exp_date,
        card_id,
        user_id,
    )

    cursor.execute(sql, params)
    connection.commit()
    connection.close()
    return True


def updateLicense(user_id, license_id, name, diverse_json):
    [connection, cursor] = connectToDatabase()

    sql = """
    UPDATE License
    SET 
        name = %s,
        diverse = %s
    WHERE 
        id = %s
        AND id IN (
            SELECT License_id 
            FROM User_License 
            WHERE Users_id = %s
        );
    """

    # 'diverse_json' should be a valid JSON string or a Python dict
    params = (name, diverse_json, license_id, user_id)

    cursor.execute(sql, params)
    connection.commit()
    connection.close()
    return True


from modules.database import connectToDatabase


def switchFavourite(user_id, item_id, category):
    # 1. Map categories to their specific Schema details
    # This handles the inconsistent naming (Password_User vs User_Notes)
    # and quotes the "Identity" table because it's a reserved keyword.
    schema_map = {
        "Password": {
            "table": "Password",
            "junction": "Password_User",
            "fk_col": "Password_id",
        },
        "Notes": {"table": "Notes", "junction": "User_Notes", "fk_col": "Notes_id"},
        "CreditCard": {
            "table": "CreditCard",
            "junction": "User_CreditCard",
            "fk_col": "CreditCard_id",
        },
        "Identity": {
            "table": '"Identity"',  # Double quotes required for reserved keyword
            "junction": "User_Identity",
            "fk_col": "identity_id",
        },
        "License": {
            "table": "License",
            "junction": "User_License",
            "fk_col": "License_id",
        },
    }

    if category not in schema_map:
        return False

    # Get the configuration for this category
    config = schema_map[category]
    table = config["table"]
    junction = config["junction"]
    fk_col = config["fk_col"]

    [connection, cursor] = connectToDatabase()

    # 2. Construct the query using f-strings for identifiers (Table/Column names)
    # and %s for values (IDs) to prevent SQL injection.
    sql = f"""
    UPDATE {table}
    SET favourite = NOT favourite
    WHERE id = %s
      AND id IN (
          SELECT {fk_col}
          FROM {junction}
          WHERE Users_id = %s
      );
    """
    try:
        cursor.execute(sql, (item_id, user_id))
        connection.commit()
        # Returns True if a row was actually found and updated
        return cursor.rowcount > 0
    except Exception as e:
        return False
    finally:
        connection.close()
