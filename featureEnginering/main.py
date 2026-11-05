import io
import os
import re #regex
import psycopg
from music21 import converter, chord
from streamFactory import getStream
from datetime import datetime

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "appdb"),
    "user": os.getenv("DB_USER", "setMaker"),
    "password": os.getenv("DB_PASSWORD", "1234"),
}

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:8333")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "setMaker")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "1234")
S3_BUCKET = os.getenv("S3_BUCKET", "features")

tunes = []

with psycopg.connect(**DB_CONFIG) as conn:
        print(conn)
        with conn.cursor() as cur: #maybe not neccesarry with cursor

            cur.execute(
                """
                SELECT *
                FROM raw.tunes
                JOIN (
                    SELECT tune_id, MIN(setting_id) AS setting_id
                    FROM raw.tunes
                    GROUP BY tune_id
                ) m USING (tune_id, setting_id);
                """
            )

            rows = cur.fetchall()  # list of tuples, one per unique tune_id
            for tune in rows:
                  tunes.append(getStream(
                        id=tune[0],
                        name=tune[1],
                        type=tune[2],
                        meter=tune[3],
                        modeRaw=tune[4],
                        ABC=tune[5],
                        date=tune[6],
                        composer=tune[7]
                  ))

Features = {}

