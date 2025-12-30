import os
import requests
import datetime


GEOIP_PATH = "/geoip/GeoLite2-Country.mmdb"
DOWNLOAD_URL = (
    "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb"
)


def get_geoip_status() -> dict:
    """Zwraca datę ostatniej modyfikacji pliku bazy."""
    if not os.path.exists(GEOIP_PATH):
        return {"exists": False, "last_modified": "Brak pliku"}

    # Pobierz czas modyfikacji pliku
    mod_time = os.path.getmtime(GEOIP_PATH)
    dt_obj = datetime.datetime.fromtimestamp(mod_time)

    return {
        "exists": True,
        "last_modified": dt_obj.strftime("%Y-%m-%d %H:%M:%S"),
        "size_mb": round(os.path.getsize(GEOIP_PATH) / (1024 * 1024), 2),
    }


def update_geoip_database() -> tuple[bool, str]:
    """Pobiera nową wersję bazy GeoIP."""
    try:
        print("GEOIP: Rozpoczynam pobieranie...", flush=True)
        response = requests.get(DOWNLOAD_URL, stream=True, timeout=30)
        response.raise_for_status()

        # Zapisujemy do pliku tymczasowego, żeby nie uszkodzić bazy w trakcie pobierania
        temp_path = GEOIP_PATH + ".tmp"

        with open(temp_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Podmieniamy plik
        os.replace(temp_path, GEOIP_PATH)
        print("GEOIP: Baza zaktualizowana pomyślnie.", flush=True)
        return True, "Baza GeoIP została zaktualizowana."

    except Exception as e:
        print(f"GEOIP Error: {e}", flush=True)
        return False, str(e)
