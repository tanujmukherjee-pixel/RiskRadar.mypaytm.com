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

    # Filter rows where tag appears in either name or description (case-insensitive)
    # Calculate BM25-like scores for name and description matches
    k1 = 1.5
    b = 0.75
    
    # Calculate average field lengths
    avg_name_len = df['name'].str.len().mean()
    avg_desc_len = df['description'].str.len().mean()
    
    # Calculate scores for name matches
    name_matches = df['name'].str.contains(identifier, case=False, na=False)
    name_scores = name_matches * (1 + k1) / (1 + k1 * ((df['name'].str.len() / avg_name_len) * b))
    
    # Calculate scores for description matches
    desc_matches = df['description'].str.contains(identifier, case=False, na=False) 
    desc_scores = desc_matches * (1 + k1) / (1 + k1 * ((df['description'].str.len() / avg_desc_len) * b))
    
    # Combine scores with higher weight for name matches
    total_scores = (name_scores * 2) + desc_scores
    
    # Filter rows with non-zero scores and add score column
    filtered_df_temp = df[total_scores > 0].copy()
    filtered_df_temp['relevance_score'] = total_scores[total_scores > 0]
    
    # Sort by score and concatenate
    filtered_df_temp = filtered_df_temp.sort_values('relevance_score', ascending=False)
    filtered_df = pd.concat([filtered_df, filtered_df_temp])

    # Remove duplicates and drop the name column
    filtered_df = filtered_df.drop_duplicates().drop('name', axis=1)
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

def fetch_all_insights():
    """
    Fetches all insights from the cdp
    """
    url = os.environ.get("PULSE_SERVICE_HOST", "https://pulse.bi.mypaytm.com") + "/api/v1/insight/?q=(filters:!((col:type,opr:eq,value:Insight)),order_column:name,order_direction:desc,page:0,page_size:200)"
    response = get_request(url, None)
    result = response["result"]
    df = pd.DataFrame(result)
    columns_to_keep = ['id', 'name', 'filter', 'granularity', 'segments', 'slices', 'time_range']
    df = df[df.columns.intersection(columns_to_keep)]
    return df.to_dict(orient="records")

def fetch_insight_details(insight_id: str, segment_id: str, time_range: str = "Last 30 days", column_filters: List[str] = [], granularity_value: str = "all"):
    """
    Fetches details of an insight from the cdp based on insight id
    default time range is last 30 days
    default column filters are empty
    default granularity is all
    """
    url = os.environ.get("PULSE_SERVICE_HOST", "https://pulse.bi.mypaytm.com") + f"/api/v1/chart/{insight_id}/data/?segment={segment_id}&time_range={time_range}&column_filters={column_filters}&insight=true&granularity={granularity_value}&isNewInsight=false&force=true"
    response = get_request(url, None)
    response = response["result"]
    df = pd.DataFrame(response)
    columns_to_keep = ['data_json']
    df = df[df.columns.intersection(columns_to_keep)]
    return df.to_dict(orient="records")