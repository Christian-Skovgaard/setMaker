CREATE SCHEMA IF NOT EXISTS raw;
SET search_path TO raw;


-- versioning
CREATE TABLE IF NOT EXISTS raw.snapshot ( --need raw.--- for not being keyword
    snapshot_id  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, --works as SERIAL
    commit_sha TEXT NOT NULL UNIQUE,
    loaded_at TIMESTAMP NOT NULL default now()
);

--tunes
CREATE TABLE IF NOT EXISTS tunes (
    tune_id     INTEGER,
    setting_id  INTEGER,
    name        TEXT NOT NULL,
    type        TEXT,
    meter       TEXT,
    mode        TEXT,
    abc         TEXT,
    date        TIMESTAMP,
    username    TEXT,
    composer    TEXT,
    snapshot_id INTEGER
);

--sets
CREATE TABLE IF NOT EXISTS tune_sets (
    tuneset       INTEGER NOT NULL,
    settingorder  INTEGER NOT NULL,
    date          TIMESTAMP,
    member_id     INTEGER,
    username      TEXT,
    name          TEXT,
    tune_id       INTEGER,
    setting_id    INTEGER,
    type          TEXT,
    meter         TEXT,
    mode          TEXT,
    abc           TEXT, --redundant
    snapshot_id INTEGER
);

--recordings
CREATE TABLE IF NOT EXISTS recordings (
    id         INTEGER,
    artist     TEXT,
    recording  TEXT,
    track      INTEGER,
    number     INTEGER,
    tune       TEXT,
    tune_id    INTEGER,   -- nullable: some rows have no tune_id
    snapshot_id INTEGER,
    PRIMARY KEY (id, track, number, snapshot_id)
);