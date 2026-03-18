import json
import os
import urllib.parse
import uuid
from datetime import datetime

import pandas as pd
import requests
from dateutil import parser

from ..utils.api import get_request, post_request

pulse_cookie = os.getenv("PULSE_COOKIE")
print(pulse_cookie)

imply_cookie = os.getenv("IMPLY_COOKIE")
print(imply_cookie)


def get_all_funnels():
    """
    Fetches all the funnels from the druid
    """

    if not pulse_cookie:
        raise ValueError("PULSE_COOKIE environment variable is not set")

    headers = {
        "Cookie": pulse_cookie,
        "Content-Type": "application/json",
    }

    funnel_reponse = get_request(
        "https://pulse.bi.mypaytm.com/api/v1/chart/list/funnelhub_viz", headers
    )
    result = [
        {
            "funnel_name": item["slice_name"],
            "goal": item["goal"],
            "vertical_name": item["vertical_name"],
            "product_name": item["product_name"],
            "id": item["id"],
        }
        for item in funnel_reponse["result"]
    ]
    return result


def fetch_query(funnel_id, funnel_name, session_id, segment_query=None):
    """
    Fetches the file path for the query for the funnel for a given segment and if not provided any segment, fetches query corresponding to the funnel across all segments
    """

    headers = {
        "Cookie": pulse_cookie,
        "Content-Type": "application/json",
    }
    query_context = get_request(
        f"https://pulse.bi.mypaytm.com/api/v1/chart/{funnel_id}", headers
    )["result"]["query_context"]

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
    query = json.loads(base_query["result"][0]["query"])
    generated_uuid = str(uuid.uuid4())
    folder_path = f"data/agents/devrev/temp/{session_id}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_path = (
        f"data/agents/devrev/temp/{session_id}/druid_query_{generated_uuid}.json"
    )
    with open(file_path, "w") as file:
        json.dump(query, file)

    print(file_path)
    return file_path


def add_segment_query(base_query, segment_query):
    """
    Adds the segment query to the base query
    """
    segments = segment_query.split(" ")

    for query in base_query["queries"]:
        for metric in query["run_time_metric"]["data"]["metrics"]:
            if segments[1] in ["IN", "NOT IN"]:
                print(segments[2])
                segments[2] = str(segments[2]).split(",")
            metric["filters"].append(
                {"col": segments[0], "op": segments[1], "val": segments[2]}
            )

    return base_query


def execute_query_pulse(file_path: str, start_date: str, end_date: str) -> dict | str:
    """
    Takes file path as input and returns result of it after querrying pulse
    Data returned corresponds to the user visits to the app for the query
    :file_path: file path of the query in json format
    :start_date: start date of the query. if not provided , ask user for the same
    :end_date: end date of the query. if not provided , ask user for the same
    :return: result of the query in json format with values as count of user visiting that page
    """
    try:

        with open(file_path, "r") as file:
            payload = json.load(file)

        api_url = "https://paytmprod.implycloud.com/p/3f93cc1e-b9d1-4bf8-9a97-87392e98cfc6/console/druid/druid/v2"

        if not imply_cookie:
            raise ValueError("IMPLY_COOKIE environment variable is not set")

        headers = {
            "Cookie": imply_cookie,
            "Content-Type": "application/json",
        }

        date_format = "%Y-%m-%dT%H:%M:%S+05:30"
        start_date = parser.parse(start_date).strftime(date_format)
        end_date = parser.parse(end_date).strftime(date_format)
        payload["intervals"] = f"{start_date}/{end_date}"
        response = post_request(api_url, headers, payload)
        return response
    except requests.RequestException as e:
        return f"Error querying Funnel Data"


def get_segment_query(segment: str, vertical: str, product: str):
    """
    Fetches the query for the segment
    """
    segments = fetch_all_applicable_segments(vertical, product)
    segment_query = segments[segments["Segment Name"] == segment]["Condition"].values[0]
    return segment_query


def fetch_all_segments():
    """
    Fetches all segments
    """
    try:
        file_path = (
            "data/agents/devrev/tools/Funnel Hub _ Definitions - Segment mapping.csv"
        )
        segments = pd.read_csv(file_path)
        segments["Condition"] = segments["Segment Definition"]
        segments.drop(columns=["Segment Definition"], inplace=True)
        return segments.to_dict(orient="records")
    except Exception as e:
        print(e)
        return f"Error fetching segments: {str(e)}"


def fetch_all_applicable_segments(vertical: str, product: str):
    """
    Fetches all applicable segments for the query
    """
    segments = fetch_all_segments()
    filtered_segments = [
        segment
        for segment in segments
        if segment["Vertical"] == vertical and segment["Product"] == product
    ]
    common_segments = [
        segment
        for segment in filtered_segments
        if segment["Vertical"] == "Common" and segment["Product"] == "Common"
    ]
    return filtered_segments + common_segments
