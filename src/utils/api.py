import requests

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def get_request(url: str, headers: dict) -> dict:
    """
    Sends a GET request to the given URL with the given headers.
    """
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()


def post_request(url: str, headers: dict, payload: dict) -> dict:
    """
    Sends a POST request to the given URL with the given headers and payload.
    """
    response = requests.post(url, headers=headers, json=payload, verify=False)
    print(response.text)
    response.raise_for_status()
    return response.json()