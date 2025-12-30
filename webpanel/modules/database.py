import psycopg2
from dotenv import load_dotenv
import os

# modules

load_dotenv()


DATABASE_DATABASE = os.getenv("DATABASE_DATABASE")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")


def connectToDatabase():
    connection = psycopg2.connect(
        database=DATABASE_DATABASE,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
    )

    cursor = connection.cursor()
    return [connection, cursor]
