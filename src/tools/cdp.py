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

def fetch_dataset_schema(dataset_id: str):
    """
    Fetches the schema of the dataset from the cdp based on dataset id fetched from fetch_all_datasets
    """
    url = os.environ.get("DATASET_SERVICE_HOST", "http://dataset-service-prod.mm7pbnhhzr.ap-south-1.elasticbeanstalk.com") + f"/v2/datasets/{dataset_id}"
    response = get_request(url, None)
    table_name = response["name"]
    fields = response["fields"]
    df = pd.DataFrame(fields)
    # Select only the specified columns if they exist in the DataFrame
    columns_to_keep = ['name', 'data_type', 'column_type', 'description', 'primary_key', 'status']
    df = df[df.columns.intersection(columns_to_keep)]
    df["schema"] = table_name
    return df.to_dict(orient="records")