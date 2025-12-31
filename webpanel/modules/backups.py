import os
import subprocess
import glob
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BACKUP_DIR = "/backups"
DB_HOST = os.getenv("DATABASE_HOST", "db")
DB_NAME = os.getenv("DATABASE_DATABASE")
DB_USER = os.getenv("DATABASE_USER")
DB_PASS = os.getenv("DATABASE_PASSWORD")
ENC_KEY = os.getenv("BACKUP_ENCRYPTION_KEY")  # Pobieramy klucz


def create_backup() -> tuple[bool, str]:
    """Creates encrypted backup of database

    Returns:
        tuple[bool, str]: [result, message | None]
    """
    print("DEBUG: Rozpoczynam tworzenie backupu...", flush=True)

    if not os.path.exists(BACKUP_DIR):
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            print(f"DEBUG: Utworzono katalog {BACKUP_DIR}", flush=True)
        except Exception as e:
            print(f"DEBUG: Błąd tworzenia katalogu: {e}", flush=True)
            return False, str(e)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"backup_{timestamp}.sql.enc"
    filepath = os.path.join(BACKUP_DIR, filename)

    print(f"DEBUG: Plik docelowy: {filepath}", flush=True)

    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASS or ""
    env["ENC_KEY"] = ENC_KEY or ""

    # Sprawdźmy czy zmienne są (nie wypisuj hasła!)
    print(f"DEBUG: DB_HOST={DB_HOST}, DB_USER={DB_USER}, DB_NAME={DB_NAME}", flush=True)

    dump_cmd = [
        "pg_dump",
        "-h",
        DB_HOST,
        "-U",
        DB_USER,
        "--clean",
        "--if-exists",
        "-d",
        DB_NAME,
    ]

    # Dodajemy -v (verbose) do openssl żeby widzieć czy działa
    enc_cmd = [
        "openssl",
        "enc",
        "-aes-256-cbc",
        "-pbkdf2",
        "-salt",
        "-pass",
        "env:ENC_KEY",
        "-v",
    ]

    try:
        with open(filepath, "wb") as outfile:
            print("DEBUG: Uruchamiam procesy...", flush=True)

            p1 = subprocess.Popen(
                dump_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
            )
            p2 = subprocess.Popen(
                enc_cmd,
                stdin=p1.stdout,
                stdout=outfile,
                stderr=subprocess.PIPE,
                env=env,
            )

            p1.stdout.close()  # type: ignore

            # Czekamy na wyniki
            _, p2_err = p2.communicate()
            _, p1_err = p1.communicate()

            print(
                f"DEBUG: Kody wyjścia -> pg_dump: {p1.returncode}, openssl: {p2.returncode}",
                flush=True,
            )

            if p1.returncode != 0:
                err = p1_err.decode("utf-8", errors="ignore")
                print(f"!!! BŁĄD PG_DUMP !!!: {err}", flush=True)
                # NIE USUWAMY PLIKU DLA CELÓW TESTOWYCH
                return False, f"Dump Error: {err}"

            if p2.returncode != 0:
                err = p2_err.decode("utf-8", errors="ignore")
                print(f"!!! BŁĄD OPENSSL !!!: {err}", flush=True)
                return False, f"Enc Error: {err}"

            # Sprawdźmy rozmiar
            size = os.path.getsize(filepath)
            print(f"DEBUG: Sukces! Rozmiar pliku: {size} bajtów", flush=True)

            return True, filename

    except Exception as e:
        print(f"DEBUG EXCEPTION: {e}", flush=True)
        return False, str(e)


def list_backups() -> list:
    """Lists all availible backup

    Returns:
        list: list with backup data
    """
    # Szukamy teraz plików z końcówką .enc
    files = glob.glob(os.path.join(BACKUP_DIR, "*.enc"))
    files.sort(key=os.path.getmtime, reverse=True)

    backups = []
    for f in files:
        stats = os.stat(f)
        backups.append(
            {
                "name": os.path.basename(f),
                "size_mb": round(stats.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stats.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        )
    return backups


def restore_backup(filename) -> tuple[bool, str]:
    """Restore database from backup

    Args:
        filename (_type_): Name of backup file

    Returns:
        tuple[bool, str]: [result, message]
    """
    filepath = os.path.join(BACKUP_DIR, os.path.basename(filename))

    if not os.path.exists(filepath):
        return False, "File not found"

    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASS or ""
    env["ENC_KEY"] = ENC_KEY or ""

    # 1. Komenda deszyfrowania (-d)
    dec_cmd = [
        "openssl",
        "enc",
        "-d",
        "-aes-256-cbc",
        "-pbkdf2",
        "-salt",
        "-pass",
        "env:ENC_KEY",
        "-in",
        filepath,
    ]

    # 2. Komenda wczytania do bazy
    psql_cmd = ["psql", "-h", DB_HOST, "-U", DB_USER, "-d", DB_NAME]

    try:
        # Krok A: Deszyfrowanie (stdout idzie do psql)
        p1 = subprocess.Popen(dec_cmd, stdout=subprocess.PIPE, env=env)

        # Krok B: PSQL (czyta z p1.stdout)
        p2 = subprocess.Popen(psql_cmd, stdin=p1.stdout, env=env)

        p1.stdout.close()  # type: ignore
        p2.communicate()

        if p2.returncode == 0:
            return True, "Success"
        else:
            return False, "Restore failed (Password incorrect or DB error)"

    except Exception as e:
        return False, str(e)


# Funkcja delete_backup pozostaje bez zmian
def delete_backup(filename) -> bool:
    """Deletes backup file

    Args:
        filename (_type_): Backup file name

    Returns:
        bool: Result of operation
    """
    safe_name = os.path.basename(filename)
    filepath = os.path.join(BACKUP_DIR, safe_name)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
