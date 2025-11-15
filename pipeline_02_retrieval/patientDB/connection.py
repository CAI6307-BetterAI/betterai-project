import os

import psycopg2
from dotenv import find_dotenv, load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv(find_dotenv())

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        cursor_factory=RealDictCursor
    )
