#
import os
import psycopg

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "appdb"),
    "user": os.getenv("DB_USER", "app"),
    "password": os.getenv("DB_PASSWORD", "secret"),
}

with psycopg.connect(**DB_CONFIG) as conn:
    print(conn)
    with conn.cursor() as cur:
        # only tunes from the newest snapshot, so no duplicates across ingests
        cur.execute(
            """
            SELECT tune_id, setting_id, name, type, meter, mode
            FROM raw.tunes
            WHERE snapshot_id = (SELECT max(snapshot_id) FROM raw.snapshot)
            """
        )
        for row in cur.fetchall():
            print(row)
