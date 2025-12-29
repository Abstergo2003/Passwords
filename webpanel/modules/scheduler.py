import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from modules.backups import create_backup

# Konfiguracja logowania, żebyś widział w konsoli, że backup się robi
logging.basicConfig()
logger = logging.getLogger("apscheduler")
logger.setLevel(logging.INFO)


def run_backup_job():
    """Funkcja wrapper, która wywołuje backup i loguje wynik."""
    print("SCHEDULER: Rozpoczynam automatyczny backup...", flush=True)
    success, msg = create_backup()
    if success:
        print(f"SCHEDULER: Sukces! Utworzono kopię: {msg}", flush=True)
    else:
        print(f"SCHEDULER: BŁĄD! Nie udało się wykonać kopii: {msg}", flush=True)


def start_scheduler():
    """Inicjalizuje i uruchamia harmonogram."""
    scheduler = BackgroundScheduler()

    # DODAWANIE ZADANIA:
    # Uruchom codziennie o 03:00 nad ranem
    # Uwaga: Czas kontenera to zazwyczaj UTC.
    # Jeśli jesteś w Polsce (UTC+1/+2), 03:00 UTC to 04:00 lub 05:00 czasu polskiego.
    scheduler.add_job(
        func=run_backup_job,
        trigger=CronTrigger(hour=3, minute=0),
        id="daily_backup_job",
        name="Tworzenie codziennej kopii bazy",
        replace_existing=True,
    )

    # Opcjonalnie: Zadanie testowe, które uruchamia się co godzinę (zakomentuj jeśli nie chcesz)
    # scheduler.add_job(run_backup_job, 'interval', hours=1)

    scheduler.start()
    print("SCHEDULER: Harmonogram został uruchomiony.", flush=True)
