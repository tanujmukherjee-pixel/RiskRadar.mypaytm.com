import requests
from datetime import datetime
from dateutil import parser
import pandas as pd
from ....utils.api import post_request, get_request
import json
import urllib.parse
import time

def get_all_funnels():
    """
    Fetches all the funnels from the druid
    """
    headers = {
            "Cookie": "_clck=1upy6g3%7C2%7Cfsx%7C0%7C1833; session=.eJwtkUuP2jAYRf9K5TWtbMfxg11KQyg00CQzA2lVoc-xTTKFBOVFYTT_vZHa5ZXu4txz39DRtbYr0bxvBztDx8qgOQLsEw7S-EJjhanPQehCF9wZBr7g4FzBFDg1tZSxnuOWK86xpAUTknpYEzDUWmIoFIQTyQVhhQDATFgsmWQaF74h2KPGV5hh4YivCzz1idSaGjRD56aAs51YbD2lBoZ-YnxDH3o0_4nuQNUnwEG69y-Cf3k-7eyK_S7LfXq4DF77Mj6VQ5gvKHnoXbjMOmP7y2tuyi0MSQVpjC2t_bUL42al9I_h2nxVVTPeO8-4upeQ59Ful3VSbM_pY21lv82Cjym-JY-RufD70Dwl0YVSuwjv7WsEuz-r8bHpPPEy8uSwbIeNvMbnpRuPt5sM6yCCxSnfBO45C9I4Wyar6EDjanH4HEf8W-1JvhagcL1PujLARPjTXvTr_f_o47VtxsrYdlJxaprT5GSGhs62_54iSmH0_hdWcoyH.Z5eFmA.zQAF7VrkccTUtDO6cI5T3fV2mtM",
            "Content-Type": "application/json",
        }

    funnel_reponse = get_request("https://pulse.bi.mypaytm.com/api/v1/chart/list/funnelhub_viz", headers)
    result = [
        {
            "funnel_name": item["slice_name"],
            "goal": item["goal"],
            "vertical_name": item["vertical_name"],
            "product_name": item["product_name"],
            "id": item["id"]
        }
        for item in funnel_reponse["result"]
    ]
    return result

def fetch_query(funnel_id, funnel_name, segment_query = None):
    """
    Fetches the query for the funnel for a given segment and if not provided any segment, fetches query corresponding to the funnel across all segments
    """
    
    headers = {
        "Cookie": "_clck=1upy6g3%7C2%7Cfsx%7C0%7C1833; session=.eJwtkUuP2jAYRf9K5TWtbMfxg11KQyg00CQzA2lVoc-xTTKFBOVFYTT_vZHa5ZXu4txz39DRtbYr0bxvBztDx8qgOQLsEw7S-EJjhanPQehCF9wZBr7g4FzBFDg1tZSxnuOWK86xpAUTknpYEzDUWmIoFIQTyQVhhQDATFgsmWQaF74h2KPGV5hh4YivCzz1idSaGjRD56aAs51YbD2lBoZ-YnxDH3o0_4nuQNUnwEG69y-Cf3k-7eyK_S7LfXq4DF77Mj6VQ5gvKHnoXbjMOmP7y2tuyi0MSQVpjC2t_bUL42al9I_h2nxVVTPeO8-4upeQ59Ful3VSbM_pY21lv82Cjym-JY-RufD70Dwl0YVSuwjv7WsEuz-r8bHpPPEy8uSwbIeNvMbnpRuPt5sM6yCCxSnfBO45C9I4Wyar6EDjanH4HEf8W-1JvhagcL1PujLARPjTXvTr_f_o47VtxsrYdlJxaprT5GSGhs62_54iSmH0_hdWcoyH.Z5eFmA.zQAF7VrkccTUtDO6cI5T3fV2mtM",
        "Content-Type": "application/json",
    }
    query_context = get_request(f"https://pulse.bi.mypaytm.com/api/v1/chart/{funnel_id}", headers)["result"]["query_context"]

    query_params = {
        "form_data": f'{{"slice_id":{funnel_id}}}',
        "slice_name": funnel_name,
        "viz_type": "funnelhub_viz",
    }
    encoded_params = urllib.parse.urlencode(query_params)
    url = f"https://pulse.bi.mypaytm.com/api/v1/chart/data?{encoded_params}"

    payload = json.loads(query_context)
    payload["result_type"] = "query"

    if segment_query:
        payload = add_segment_query(payload, segment_query)
    base_query = post_request(url, headers, payload)
    return json.loads(base_query["result"][0]["query"])

def add_segment_query(base_query, segment_query):
    """
    Adds the segment query to the base query
    """
    segments = segment_query.split(" ")

    for query in base_query["queries"]:
        for metric in query["run_time_metric"]["data"]["metrics"]:
            metric["filters"].append({"col" : segments[0], "op" : segments[1], "val" : segments[2]})
    return base_query


def execute_query_pulse(basequery: str, start_date: str, end_date: str) -> str:
    """
    Takes query as json input and returns result of it after querrying pulse
    Data returned corresponds to the user visits to the app for the query
    :query: druid query in json format
    :segment: segment to be applied to the query
    :start_date: start date of the query in format "2025-01-01T00:00:00+05:30"
    :end_date: end date of the query in format "2025-01-22T00:00:00+05:30"
    :return: result of the query in json format with values as count of user visiting that page
    """ 
    try:
        api_url = "https://paytmprod.implycloud.com/p/3f93cc1e-b9d1-4bf8-9a97-87392e98cfc6/console/druid/druid/v2"
        
        headers = {
            "Cookie": "connect.sid=s%3AWmz6QbXicl0HceKt7A1tpn3Nf0ytxqqp.VcjszXj2l%2B3EGpKCCPDixB4bSSltp4IjkNTyENkpEpg",
            "Content-Type": "application/json",
        }

        date_format = '%Y-%m-%dT%H:%M:%S+05:30'
        start_date = parser.parse(start_date).strftime(date_format)
        end_date = parser.parse(end_date).strftime(date_format)

        payload = json.loads(basequery)
        response = post_request(api_url, headers, payload)
        return response
    except requests.RequestException as e:
        print(e)
        return f"Error querying pulse: {str(e)}"
    
def get_segment_query(segment: str, vertical: str, product: str):
    """
    Fetches the query for the segment
    """
    segments = fetch_all_segments(vertical, product)
    segment_query = segments[segments["Segment Name"] == segment]["Condition"].values[0]
    return segment_query

def fetch_all_segments(vertical: str, product: str):
    """
    Fetches all relevant segments for the query
    """
    try:
        file_path = "data/agents/devrev/tools/Funnel Hub _ Definitions - Segment mapping.csv"
        segments = pd.read_csv(file_path)
        segments["Condition"] = segments["Segment Definition"]
        segments.drop(columns=["Segment Definition"], inplace=True)
        filtered_segments = segments[(segments["Vertical"] == vertical) & (segments["Product"] == product)]
        return filtered_segments.to_dict(orient="records")
    except Exception as e:
        print(e)
        return f"Error fetching segments: {str(e)}"