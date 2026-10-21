-- with fire
TRUNCATE TABLE
    raw.snapshot,
    raw.tunes,
    raw.tune_sets,
    raw.recordings
RESTART IDENTITY CASCADE;
