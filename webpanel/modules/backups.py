import os
import subprocess
import glob
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BACKUP_DIR = "/backups"

# Pobieramy dane z ENV (te same, których używa aplikacja)
DB_HOST = os.getenv("DATABASE_HOST", "db")
DB_NAME = os.getenv("DATABASE_DATABASE")
DB_USER = os.getenv("DATABASE_USER")
DB_PASS = os.getenv("DATABASE_PASSWORD")
BACKUP_DIR = "/backups"


def create_backup():
    """Tworzy nowy plik .sql z zrzutem bazy."""
    if not os.path.exists(BACKUP_DIR):
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
        except Exception as e:
            return (
                False,
                f"Permission Error: Cannot create directory {BACKUP_DIR}. {str(e)}",
            )
    # ------------------------------------------

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"backup_{timestamp}.sql"
    filepath = os.path.join(BACKUP_DIR, filename)

    # Komenda pg_dump
    # PGPASSWORD przekazujemy jako zmienną środowiskową dla bezpieczeństwa
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASS

    # Flaga --clean dodaje polecenia DROP, co ułatwia przywracanie
    cmd = [
        "pg_dump",
        "-h",
        DB_HOST,
        "-U",
        DB_USER,
        "--clean",
        "--if-exists",
        "-d",
        DB_NAME,
        "-f",
        filepath,
    ]

    try:
        subprocess.run(cmd, env=env, check=True)
        return True, filename
    except subprocess.CalledProcessError as e:
        print(f"Backup Error: {e}")
        return False, str(e)


def list_backups():
    """Zwraca listę dostępnych plików backupu."""
    print(f"DEBUG: Szukam w {BACKUP_DIR}")
    print(f"DEBUG: Zawartość katalogu: {os.listdir(BACKUP_DIR)}")
    files = glob.glob(os.path.join(BACKUP_DIR, "*.sql"))
    # Sortujemy od najnowszych
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


def delete_backup(filename):
    """Usuwa plik backupu."""
    # Zabezpieczenie przed Directory Traversal ("../../etc/passwd")
    safe_name = os.path.basename(filename)
    filepath = os.path.join(BACKUP_DIR, safe_name)

    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def restore_backup(filename):
    """
    Przywraca bazę z pliku.
    UWAGA: To nadpisze obecne dane!
    """
    safe_name = os.path.basename(filename)
    filepath = os.path.join(BACKUP_DIR, safe_name)

    if not os.path.exists(filepath):
        return False, "File not found"

    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASS

    # Używamy psql do wczytania pliku
    # < filepath robimy otwierając plik w Pythonie
    cmd = ["psql", "-h", DB_HOST, "-U", DB_USER, "-d", DB_NAME]

    try:
        with open(filepath, "r") as f:
            subprocess.run(cmd, env=env, stdin=f, check=True)
        return True, "Success"
    except Exception as e:
        return False, str(e)
