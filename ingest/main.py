#Script for getting raw data from thesession.org to postgres
import os
import json
import subprocess #for running other programs like sh
from pathlib import Path
import psycopg
import sys

theSessionDataParthString = os.getenv("SESSIONDATAPARTH", "/home/cello/Documents/study/mlOps/TheSession-data/") #make a shorter name

commitSha = subprocess.run( #gets sha from repo by checking head in dir, so not fetch from process when building anymore.
    ["git", "-C", theSessionDataParthString, "rev-parse", "HEAD"],
    capture_output=True, text=True, check=True,
).stdout.strip()

# json import
recordingsJSON = json.loads(Path(theSessionDataParthString,"json","recordings.json").read_text(encoding="utf-8"))
tunesJSON = json.loads(Path(theSessionDataParthString,"json","tunes.json").read_text(encoding="utf-8"))
setsJSON = json.loads(Path(theSessionDataParthString,"json","sets.json").read_text(encoding="utf-8"))


DB_CONFIG = { #make secret 🤫
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "appdb"),
    "user": os.getenv("DB_USER", "app"),
    "password": os.getenv("DB_PASSWORD", "secret"),
}


with psycopg.connect(**DB_CONFIG) as conn:
    print(conn)
    with conn.cursor() as cur: #with conn makes commit together and roll all back on error!

        # check if commitsha is same, so no duplicate datasets.
        cur.execute("SELECT snapshot_id FROM raw.snapshot WHERE commit_sha = %s", (commitSha,))
        if cur.fetchone() is not None: #why no "!" in py 😡
            print(f"commit {commitSha} is already represented, stopping.")
            raise SystemExit(0) #kill all process and return 0

        #make new snapsht row
        cur.execute(
            "INSERT INTO raw.snapshot (commit_sha) VALUES (%s) RETURNING snapshot_id", #give new id as return
            (commitSha,),
        )
        snapshotId = cur.fetchone()[0]
        print(f"loading snapshot {snapshotId} as commit {commitSha}")

        #recordings
        recordingsVList = [
            (
                v.get("id") or None, 
                v.get("artist") or None, 
                v.get("recording") or None, 
                v.get("track") or None, 
                v.get("number")or None, 
                v.get("tune") or None, 
                v.get("tune_id") or None, 
                snapshotId
            ) for v in recordingsJSON 
        ]   
        cur.executemany(
            "INSERT INTO raw.recordings (id, artist, recording, track, number, tune, tune_id, snapshot_id)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            recordingsVList,
        )

        #tunes
        tunesVList = [
            (
                v.get("tune_id") or None,
                v.get("setting_id") or None,
                v.get("name") or None,
                v.get("type") or None,
                v.get("meter") or None,
                v.get("mode") or None,
                v.get("abc") or None,
                v.get("date") or None,
                v.get("username") or None,
                v.get("composer") or None,
                snapshotId
            ) for v in tunesJSON
        ]
        cur.executemany(
            "INSERT INTO raw.tunes (tune_id, setting_id, name, type, meter, mode, abc, date, username, composer, snapshot_id)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            tunesVList,
        )

        #sets
        setsVList = [
            (
                v.get("tuneset") or None,
                v.get("settingorder") or None,
                v.get("date") or None,
                v.get("member_id") or None,
                v.get("username") or None,
                v.get("name") or None,
                v.get("tune_id") or None,
                v.get("setting_id") or None,
                v.get("type") or None,
                v.get("meter") or None,
                v.get("mode") or None,
                v.get("abc") or None,
                snapshotId
            ) for v in setsJSON
        ]
        cur.executemany(
            "INSERT INTO raw.sets (tuneset, settingorder, date, member_id, username, name, tune_id, setting_id, type, meter, mode, abc, snapshot_id)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            setsVList,
        )

print("data ingestion complete!")
