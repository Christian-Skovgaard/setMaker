#!/usr/bin/env bash
# Wipe and restart only the postgres service (rawDataStore), the app containers are left alone
set -e
cd "$(dirname "$0")" # so it works from any directory

# compose names volumes <project>_<volume>, project defaults to the folder name
dbVolume="${COMPOSE_PROJECT_NAME:-$(basename "$PWD")}_raw_data"
dbVolume="${dbVolume,,}" # compose lowercases project names (setMaker -> setmaker)

docker compose rm --stop --force rawDataStore # stop and delete the postgres container
docker volume rm --force "$dbVolume" # delete the db data so init.sql runs again
docker compose up --force-recreate rawDataStore # fresh postgres, without starting ingest
