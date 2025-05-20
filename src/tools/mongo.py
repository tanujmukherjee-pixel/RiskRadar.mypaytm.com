import requests
from datetime import datetime
from dateutil import parser
import pandas as pd
from ..utils.api import async_get_request

async def execute_query_mongo(funnel_id: str, start_date: str, end_date: str) -> str:
    """
    Takes funnel id as input and returns result of it after querrying mongo
    Data returned corresponds to the user visits to the app for the query
    :funnel_id: funnel id of the query
    :start_date: start date of the query. if not provided , ask user for the same
    :end_date: end date of the query. if not provided , ask user for the same
    :return: result of the query in json format with values as count of user visiting that page
    """ 
    try:

        
        headers = {
            # "Cookie": "connect.sid=s%3AWmz6QbXicl0HceKt7A1tpn3Nf0ytxqqp.VcjszXj2l%2B3EGpKCCPDixB4bSSltp4IjkNTyENkpEpg",
            "Content-Type": "application/json",
        }

        date_format = '%Y-%m-%d'
        start_date = parser.parse(start_date).strftime(date_format)
        end_date = parser.parse(end_date).strftime(date_format)
        api_url = f"https://pulse-historical-service.internal.production.cdst.cdp.mypaytm.com/v1/funnel/{funnel_id}?startDate={start_date}&endDate={end_date}&granularity=P1D"

        response = await async_get_request(api_url, headers)
        return response
    except requests.RequestException as e:
        return f"Error querying Funnel Data: {str(e)}"
    