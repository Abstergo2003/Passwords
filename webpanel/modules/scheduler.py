import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from modules.backups import create_backup
from modules.geoip_utils import update_geoip_database

# Konfiguracja logowania
logging.basicConfig()
logger = logging.getLogger("apscheduler")
logger.setLevel(logging.INFO)


def run_backup_job():
    """Wrapper function to create backup"""
    print("SCHEDULER: Rozpoczynam automatyczny backup...", flush=True)
    success, msg = create_backup()
    if success:
        print(f"SCHEDULER: Sukces! Utworzono kopię: {msg}", flush=True)
    else:
        print(f"SCHEDULER: BŁĄD! Nie udało się wykonać kopii: {msg}", flush=True)


def run_geoip_update_job():
    """Wrapper function to update geoip file"""
    print("SCHEDULER: Sprawdzam aktualizacje bazy GeoIP...", flush=True)
    success, msg = update_geoip_database()
    if success:
        print(f"SCHEDULER: GeoIP Sukces! {msg}", flush=True)
    else:
        print(f"SCHEDULER: GeoIP BŁĄD! {msg}", flush=True)


def start_scheduler():
    """Initalizes and starts scheduler"""
    scheduler = BackgroundScheduler()

    # Task 1: Database backup
    # Everydar at 03:00
    scheduler.add_job(
        func=run_backup_job,
        trigger=CronTrigger(hour=3, minute=0),
        id="daily_backup_job",
        name="Tworzenie codziennej kopii bazy",
        replace_existing=True,
    )
    # first run for anyone downloadiung project
    run_geoip_update_job()
    # Task 2: GeoIP update
    # Once a week (Thursday 04:00)
    scheduler.add_job(
        func=run_geoip_update_job,
        trigger=CronTrigger(day_of_week="wed", hour=4, minute=0),
        id="weekly_geoip_update",
        name="Aktualizacja bazy GeoIP",
        replace_existing=True,
    )

    scheduler.start()
    print("SCHEDULER: Harmonogram został uruchomiony (Backup + GeoIP).", flush=True)
