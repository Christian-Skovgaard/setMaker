import io
import os
from dotenv import load_dotenv, find_dotenv
import boto3
import pandas as pd
import psycopg
from botocore.config import Config

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

# A->B->C becomes A->B and B->C. LAG gives the previous tune in the same set/track.
# Only tune_id is used as identity. Rows are first collapsed to one per tune per
# position, so several versions of a tune in one position count once.
PAIRS_SQL = """
WITH snap AS (SELECT max(snapshot_id) AS id FROM raw.snapshot),

set_tunes AS (  -- one row per tune per set position, with the set's date
    SELECT tuneset, settingorder, tune_id, min(date) AS date
    FROM raw.sets, snap
    WHERE snapshot_id = snap.id AND tune_id IS NOT NULL
    GROUP BY tuneset, settingorder, tune_id
),
set_pairs AS (
    SELECT LAG(tune_id) OVER w AS from_tune_id, tune_id AS to_tune_id, date
    FROM set_tunes
    WINDOW w AS (PARTITION BY tuneset ORDER BY settingorder)
),

-- a NULL tune_id in a track breaks the chain: its neighbours are not adjacent
rec_tunes AS (
    SELECT r.id AS rec_id, r.track, r.number, r.tune_id,
           count(*) FILTER (WHERE r.tune_id IS NULL)
               OVER (PARTITION BY r.id, r.track ORDER BY r.number) AS gap
    FROM raw.recordings r, snap
    WHERE r.snapshot_id = snap.id
),
rec_pairs AS (
    SELECT LAG(tune_id) OVER w AS from_tune_id, tune_id AS to_tune_id
    FROM rec_tunes
    WHERE tune_id IS NOT NULL
    WINDOW w AS (PARTITION BY rec_id, track, gap ORDER BY number)
),

all_pairs AS (
    SELECT from_tune_id, to_tune_id, date, 1 AS is_set FROM set_pairs
    UNION ALL
    SELECT from_tune_id, to_tune_id, NULL, 0 FROM rec_pairs
)
SELECT from_tune_id,
       to_tune_id,
       sum(is_set)::int      AS n_sets,
       sum(1 - is_set)::int  AS n_recordings,
       min(date)             AS first_seen,
       (SELECT id FROM snap) AS snapshot_id
FROM all_pairs
WHERE from_tune_id IS NOT NULL
  AND from_tune_id <> to_tune_id
GROUP BY from_tune_id, to_tune_id
ORDER BY from_tune_id, to_tune_id;
"""


def build_pairs() -> pd.DataFrame:
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(PAIRS_SQL)
            cols = [d.name for d in cur.description]
            return pd.DataFrame(cur.fetchall(), columns=cols)


def upload(df: pd.DataFrame, snapshot_id: int) -> str:
    s3 = boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        region_name="us-east-1",
        config=Config(s3={"addressing_style": "path"}),
    )
    key = f"labels/snapshot_id={snapshot_id}/pairs.parquet"
    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=buf.getvalue())
    return f"s3://{S3_BUCKET}/{key}"


def main():
    df = build_pairs()
    if df.empty:
        print("no pairs found")
        return
    snapshot_id = int(df["snapshot_id"].iloc[0])
    print(f"{len(df)} distinct pairs from snapshot {snapshot_id}")
    print(df.head(10))
    print("uploaded", upload(df, snapshot_id))


if __name__ == "__main__":
    main()
