# Używamy lekkiego obrazu Python
FROM python:3.11-slim

# Ustawiamy katalog roboczy w kontenerze
WORKDIR /app

# Instalujemy zależności systemowe (wymagane np. dla biblioteki psycopg2 do Postgresa)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Kopiujemy plik z wymaganiami (najpierw tylko to, żeby wykorzystać cache Dockera)
COPY requirements.txt .

# Instalujemy zależności Pythona
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy resztę kodu aplikacji
COPY . .

# Tworzymy użytkownika 'appuser', żeby nie uruchamiać serwera jako root (Best Practice)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Otwieramy port 5000
EXPOSE 5000

# Komenda startowa (używamy Gunicorn dla produkcji zamiast deweloperskiego serwera Flask)
# Jeśli nie masz gunicorna w requirements.txt, dodaj go: pip install gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "server:app"]