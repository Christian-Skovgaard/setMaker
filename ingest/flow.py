from prefect import flow
from main import main      # whatever your service currently runs

@flow(name="ingest-flow", log_prints=True, retries=0)
def ingest_flow():
    main()

# flow keept in different file for easy main.py debugging