"""
Registers the weekly orchestrator with Prefect.
Run inside the orchestrator image (cwd = /app):  python weekly.py
This is the only deployment with a schedule.
"""
from prefect.schedules import Cron

from flow import weekly_pipeline

if __name__ == "__main__":
    weekly_pipeline.deploy(
        name="weekly",
        work_pool_name="docker-pool",
        image="setmaker-weekly:latest",
        build=False,
        push=False,
        schedule=Cron("0 6 * * 1", timezone="Europe/Amsterdam"),  # Mondays 06:00
        job_variables={
            "image_pull_policy": "Never",
            "networks": ["setmaker_default"],      # reach prefect-server by service name
            "auto_remove": True,
        },
    )