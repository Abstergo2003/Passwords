import psutil
import requests
import json
from pyquery import PyQuery  # type: ignore
from modules.database import connectToDatabase


def check_inbucket_health():
    """Sprawdza czy kontener mailowy żyje"""
    try:
        # Wewnątrz sieci Dockerowej łączymy się po nazwie serwisu 'mail'
        r = requests.get("http://mail:9000/status", timeout=1)
        return r.status_code == 200
    except:
        return False


def check_frp_health():
    """
    Sprawdza czy tunele FRP są aktywne, odpytując Admin UI.
    """
    try:
        # Łączymy się z kontenerem 'frpc' (zdefiniowanym w docker-compose)
        response = requests.get("http://frpc:7400/api/status", timeout=1)
        if response.status_code == 200:
            data = json.loads(response.text)
            for conn in data["tcp"]:
                if conn["status"] != "running":
                    return False
            else:
                return True
    except Exception as e:
        print(f"FRP Check Error: {e}")  # Opcjonalnie do debugowania
        return False


# --- STATYSTYKI ---
def get_dashboard_data():
    data = {}

    # --- 1. HEALTHCHECK (INFRASTRUKTURA) ---
    # To jest sekcja, którą chciałeś przywrócić
    try:
        data["cpu"] = psutil.cpu_percent(interval=0.1)
        data["ram"] = psutil.virtual_memory().percent
        # data['disk'] = psutil.disk_usage('/').percent # Opcjonalne
        data["mail_service"] = check_inbucket_health()
        data["frp_tunnel"] = check_frp_health()
    except Exception as e:
        print(f"Error reading system stats: {e}")
        data["cpu"] = 0
        data["ram"] = 0
        data["mail_service"] = False

    # --- 2. BAZA DANYCH I STATYSTYKI ---
    [conn, cursor] = connectToDatabase()

    if conn:
        data["db_status"] = True
        try:
            # A. Liczenie WSZYSTKICH elementów (Total Items)
            # Lista tabel, które przechowują dane użytkownika
            # Identity musi być w cudzysłowie, bo to słowo kluczowe SQL
            tables = ["Password", "Notes", "CreditCard", '"Identity"', "License"]

            total_items = 0
            breakdown = (
                {}
            )  # Słownik do przechowywania szczegółów np. {'Password': 50, 'Notes': 10}

            for table in tables:
                clean_name = table.replace(
                    '"', ""
                )  # Usuwamy cudzysłów dla klucza w słowniku
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                breakdown[clean_name] = count
                total_items += count

            data["total_items"] = total_items
            data["items_breakdown"] = (
                breakdown  # Przekazujemy też szczegóły, żeby wyświetlić je w dymku/podpisie
            )

            # B. Inne statystyki
            cursor.execute("SELECT COUNT(*) FROM Users;")
            data["total_users"] = cursor.fetchone()[0]

            # Średnia długość hasła
            cursor.execute("SELECT AVG(LENGTH(password)) FROM Password;")
            avg_len = cursor.fetchone()[0]
            data["avg_password_len"] = round(avg_len, 1) if avg_len else 0

            # Top Domena
            cursor.execute(
                """
                SELECT domain, COUNT(*) as c 
                FROM Password 
                GROUP BY domain 
                ORDER BY c DESC 
                LIMIT 1;
            """
            )
            top_domain = cursor.fetchone()
            data["top_domain"] = top_domain[0] if top_domain else "Brak"

            # C. Lista użytkowników (do zarządzania)
            cursor.execute("SELECT id, email, tfaCode FROM Users;")
            users_list = []
            for row in cursor.fetchall():
                users_list.append(
                    {"id": row[0], "email": row[1], "has_2fa": bool(row[2])}
                )
            data["users_list"] = users_list

        except Exception as e:
            print(f"Błąd SQL w Dashboardzie: {e}")
            data["users_list"] = []
            data["total_items"] = 0
        finally:
            conn.close()
    else:
        data["db_status"] = False
        data["users_list"] = []
        data["total_items"] = 0

    return data


# --- ZARZĄDZANIE (DELETE) ---
def delete_user_fully(user_id_to_delete):
    """
    Usuwa użytkownika i kaskadowo wszystkie jego dane.
    Musi usunąć wpisy z tabel łącznikowych ORAZ właściwych tabel z danymi.
    """
    [conn, cursor] = connectToDatabase()
    if not conn:
        return False

    try:
        # Lista kategorii do wyczyszczenia
        # Struktura: (TabelaGłówna, TabelaŁącznikowa, NazwaKolumnyID)
        categories = [
            ("Password", "Password_User", "Password_id"),
            ("Notes", "User_Notes", "Notes_id"),
            ("CreditCard", "User_CreditCard", "CreditCard_id"),
            (
                '"Identity"',
                "User_Identity",
                "Identity_id",
            ),  # Cudzysłów bo Identity to keyword
            ("License", "User_License", "License_id"),
        ]

        for table, junction, fk_col in categories:
            # 1. Znajdź ID przedmiotów należących do usera
            cursor.execute(
                f"SELECT {fk_col} FROM {junction} WHERE Users_id = %s",
                (user_id_to_delete,),
            )
            item_ids = [row[0] for row in cursor.fetchall()]

            if item_ids:
                # Zamiana listy ID na format SQL tuple: ('id1', 'id2')
                ids_tuple = tuple(item_ids)

                # 2. Usuń z tabeli łącznikowej
                cursor.execute(
                    f"DELETE FROM {junction} WHERE Users_id = %s", (user_id_to_delete,)
                )

                # 3. Usuń z tabeli głównej (tylko te ID, które znaleźliśmy)
                # Hack dla jednoelementowej krotki w Pythonie (dodaje przecinek)
                if len(ids_tuple) == 1:
                    cursor.execute(f"DELETE FROM {table} WHERE id = '{ids_tuple[0]}'")
                else:
                    cursor.execute(f"DELETE FROM {table} WHERE id IN {ids_tuple}")

        # 4. Na końcu usuń samego użytkownika
        cursor.execute("DELETE FROM Users WHERE id = %s", (user_id_to_delete,))

        conn.commit()
        return True

    except Exception as e:
        print(f"CRITICAL DELETE ERROR: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
