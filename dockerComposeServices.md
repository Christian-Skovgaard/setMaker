# DB's
## rawDataStore
This where the raw unfiltered data is stored, and catalouged based on snapshot_id
PostgreSQL db.
## featurestore
seaweedfs is an opensource datastore that uses the s3 protocol
# Util
## prefect worker
intended for horizontal scalebility with the ability to add more, here we only use one because of it's ability to start and stop containers after one another as required by our pipelines.
works as a docker socket