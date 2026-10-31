#
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import psycopg

load_dotenv(find_dotenv()) #for testing!

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "appdb"),
    "user": os.getenv("DB_USER", "setMaker"),
    "password": os.getenv("DB_PASSWORD", "2138c5b8bc04048dd56e0766f17792b565f0a25725814e9089553995223e7c22"),
}

with psycopg.connect(**DB_CONFIG) as conn:
    print(conn)
    with conn.cursor() as cur:
        # only tunes from the newest snapshot, so no duplicates across ingests
        cur.execute(
            """
            SELECT tuneset, settingorder, date, tune_id, setting_id
            FROM raw.SETS
            WHERE snapshot_id = (SELECT max(snapshot_id) FROM raw.SNAPSHOT)
            LIMIT 10;
            """
        )
        for row in cur.fetchall():
            print(row)
