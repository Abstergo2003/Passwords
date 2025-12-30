from modules.database import connectToDatabase


def getPassword(user_id: str, password_id: str) -> dict:
    [connection, cursor] = connectToDatabase()
    sql = """
        SELECT 
            p.id,
            p.email,
            p.login,
            p.password,
            p.domain,
            p.tfa
        FROM 
            Password p
        JOIN 
            Password_User pu ON p.id = pu.Password_id
        WHERE 
            pu.Users_id = %s 
            AND p.id = %s;
    """
    cursor.execute(sql, (user_id, password_id))
    items = cursor.fetchall()
    if len(items) == 0:
        return {}

    item = items[0]
    connection.close()
    return item


def getNote(user_id: str, note_id: str) -> dict:
    [connection, cursor] = connectToDatabase()
    sql = """
        SELECT 
            p.id,
            p.name,
            p.content
        FROM 
            Notes p
        JOIN 
            User_Notes pu ON p.id = pu.Notes_id
        WHERE 
            pu.Users_id = %s 
            AND p.id = %s;
    """
    cursor.execute(sql, (user_id, note_id))
    items = cursor.fetchall()
    if len(items) == 0:
        return {}

    item = items[0]
    connection.close()
    return item


def getLicense(user_id: str, license_id: str) -> dict:
    [connection, cursor] = connectToDatabase()
    sql = """
        SELECT 
            p.id,
            p.name,
            p.diverse
        FROM 
            License p
        JOIN 
            User_License pu ON p.id = pu.License_id
        WHERE 
            pu.Users_id = %s 
            AND p.id = %s;
    """
    cursor.execute(sql, (user_id, license_id))
    items = cursor.fetchall()
    if len(items) == 0:
        return {}

    item = items[0]
    connection.close()
    return item


def getIdentity(user_id: str, identity_id: str) -> dict:
    [connection, cursor] = connectToDatabase()
    sql = """
        SELECT 
            p.id,
            p.name,
            p.surname,
            p.country,
            p.state,
            p.city,
            p.street,
            p.number
        FROM 
            "Identity" p
        JOIN 
            User_Identity pu ON p.id = pu.Identity_id
        WHERE 
            pu.Users_id = %s 
            AND p.id = %s;
    """
    cursor.execute(sql, (user_id, identity_id))
    items = cursor.fetchall()
    if len(items) == 0:
        return {}

    item = items[0]
    connection.close()
    return item


def getCreditCard(user_id: str, note_id: str) -> dict:
    [connection, cursor] = connectToDatabase()
    sql = """
        SELECT 
            p.id,
            p.bankName,
            p.number,
            p.brand,
            p.cvv,
            p.owner,
            p.expDate
        FROM 
            CreditCard p
        JOIN 
            User_CreditCard pu ON p.id = pu.CreditCard_id
        WHERE 
            pu.Users_id = %s 
            AND p.id = %s;
    """
    cursor.execute(sql, (user_id, note_id))
    items = cursor.fetchall()
    if len(items) == 0:
        return {}

    item = items[0]
    connection.close()
    return item
