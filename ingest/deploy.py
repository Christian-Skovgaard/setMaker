"""
Registers the ingest job with Prefect.
Run inside the ingest image (cwd = /app):  python -m deployments.deploy_ingest
No schedule here: the weekly orchestrator triggers this deployment.
"""
import os

from flow import ingest_flow

# Variables the ingest job needs at run time; copied from this container's environment
JOB_ENV_KEYS = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD", "SESSIONDATAPARTH"]

if __name__ == "__main__":
    ingest_flow.deploy(
        name="ingest",
        work_pool_name="docker-pool",
        image="setmaker-ingest:latest",
        build=False,
        push=False,
        job_variables={
            "image_pull_policy": "Never",          # use the locally built image
            "networks": ["setmaker_default"],      # reach postgres by service name
            "auto_remove": True,                   # remove the container after the run
            "env": {k: os.environ[k] for k in JOB_ENV_KEYS if k in os.environ},
            # keep the TheSession-data clone between runs (git pull instead of a full clone)
            "volumes": ["setmaker_ingest_repo:/app/TheSession-data"],
        },
    )