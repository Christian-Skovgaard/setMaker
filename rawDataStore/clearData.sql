-- with fire
TRUNCATE TABLE
    raw.snapshot,
    raw.tunes,
    raw.sets,
    raw.recordings
RESTART IDENTITY CASCADE;
