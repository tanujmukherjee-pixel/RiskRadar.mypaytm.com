import pandas as pd
from ..utils.api import get_request
from typing import List
import os

session_map = {}


def fetch_all_datasets(regex: str):
    """
    Fetches all the relevant datasets from the cdp based on regex.
    """

    keywords = regex.split()
    results = []

    for keyword in keywords:
        url = os.environ.get("DATASET_SERVICE_HOST", "http://dataset-service-prod.mm7pbnhhzr.ap-south-1.elasticbeanstalk.com") + "/v2/datasets"
        response = get_request(url, None)
        df = pd.DataFrame(response)
        # Filter for active status and select required columns
        df = df[df['status'] == 'ACTIVE'][['id', 'name', 'description']]

        filtered_df = pd.DataFrame()
        filtered_df = df[df['name'].str.contains(keyword, case=False, na=False) | df['description'].str.contains(keyword, case=False, na=False)]
        results.extend(filtered_df.to_dict(orient="records"))
    
    return results

def fetch_schema_name_from_dataset_id(dataset_id: str):
    """
    Fetches the schema from the dataset id fetched from fetch_all_datasets
    """
    base_url = os.environ.get("DATASET_SERVICE_HOST", "http://dataset-service-prod.mm7pbnhhzr.ap-south-1.elasticbeanstalk.com") + f"/v2/datasets/"
    url = base_url + dataset_id
    response = get_request(url, None)

    if "fields" not in response or response["fields"] is None:
        url = base_url + str(response["id"])
        response = get_request(url, None)
    
    destinations = response["destinations"]
    fields = response["fields"]
    filtered_fields = []
    for field in fields:
        filtered_fields.append({
            "name": field["name"],
            "description": field.get("description", ""),
            "data_type": field["data_type"]
        })
    name = "Schema Name not found"
    for destination in destinations:
        if destination["dest_type"] == "HIVE":
            name = destination["local_name"]
            break
    return {"name": name, "fields": filtered_fields}