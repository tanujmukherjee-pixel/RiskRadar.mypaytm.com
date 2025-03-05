import pandas as pd
from ..utils.api import get_request

def fetch_all_relevant_tables(domain: str):
    """
    Fetches all the relevant tables from the cdp based on domain
    """
    url = f"http://dataset-service-prod.mm7pbnhhzr.ap-south-1.elasticbeanstalk.com/v2/datasets"
    response = get_request(url, None)
    df = pd.DataFrame(response)
    # Filter for active status and select required columns
    df = df[df['status'] == 'ACTIVE'][['id', 'name', 'description']]

    # Filter rows where tag appears in either name or description (case-insensitive)
    df = df[df['name'].str.contains(domain, case=False, na=False) | 
            df['description'].str.contains(domain, case=False, na=False)]

    return df.to_dict(orient="records")

def fetch_table_schema(id: str):
    """
    Fetches the schema of the table from the cdp
    """
    url = f"http://dataset-service-prod.mm7pbnhhzr.ap-south-1.elasticbeanstalk.com/v2/datasets/{id}"
    response = get_request(url, None)
    fields = response["fields"]
    df = pd.DataFrame(fields)
    # Select only the specified columns if they exist in the DataFrame
    columns_to_keep = ['name', 'data_type', 'column_type', 'description', 'primary_key', 'status']
    df = df[df.columns.intersection(columns_to_keep)]
    return df.to_dict(orient="records")
