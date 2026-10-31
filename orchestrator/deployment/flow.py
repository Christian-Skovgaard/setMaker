from prefect import flow
from prefect.deployments import run_deployment


def run_and_check(name: str):
    run = run_deployment(name)  # blocks until the run finishes
    if not run.state.is_completed():
        raise RuntimeError(f"{name} ended in state {run.state.name}")


@flow(name="weekly-pipeline", log_prints=True)
def weekly_pipeline():
    run_and_check("ingest-flow/ingest")
    # run_and_check("labeling-flow/labeling")   # add once labeling has a deployment
