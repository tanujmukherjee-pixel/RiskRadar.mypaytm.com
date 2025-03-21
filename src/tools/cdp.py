import pandas as pd
from ..utils.api import get_request
from typing import List
import os

session_map = {}


def fetch_all_datasets(identifier: str, session_id: str):
    """
    Fetches all the relevant datasets from the cdp based on tags
    """
    if session_id in session_map:
        return session_map[session_id]

    url = os.environ.get("DATASET_SERVICE_HOST", "http://dataset-service-prod.mm7pbnhhzr.ap-south-1.elasticbeanstalk.com") + "/v2/datasets"
    response = get_request(url, None)
    df = pd.DataFrame(response)
    # Filter for active status and select required columns
    df = df[df['status'] == 'ACTIVE'][['id', 'name', 'description']]

    filtered_df = pd.DataFrame()
    filtered_df = df[df['name'].str.contains(identifier, case=False, na=False) | df['description'].str.contains(identifier, case=False, na=False)]
    
    return filtered_df.to_dict(orient="records")

def fetch_schema_name_from_dataset_id(dataset_id: str):
    """
    Fetches the schema name from the dataset id fetched from fetch_all_datasets
    """
    url = os.environ.get("DATASET_SERVICE_HOST", "http://dataset-service-prod.mm7pbnhhzr.ap-south-1.elasticbeanstalk.com") + f"/v2/datasets/{dataset_id}"
    response = get_request(url, None)
    destinations = response["destinations"]
    name = "Schema Name not found"
    for destination in destinations:
        if destination["dest_type"] == "HIVE":
            name = destination["local_name"]
            break
    return name