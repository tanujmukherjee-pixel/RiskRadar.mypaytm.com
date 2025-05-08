from ..utils.api import get_request
from ..constants.rule_admin import RULE_ADMIN_URL, RULE_ADMIN_TOKEN
from ..utils.auth import generate_token_for_user_email
from typing import Optional
from ..constants.kibana import REQUEST_PAYLOAD_FIELDS, REQUEST_METADATA_FIELDS, BASE_FIELDS
from .kibana import fetch_logs_timerange
from datetime import datetime, timedelta

def fetch_rule_info(rule_name: str, rule_version: str, source: str):
    """
    Fetch rule info from the rule admin service using the rule name, rule version and source.
    """

    token = generate_token_for_user_email(disable_ssl_verification=True)

    RULE_ADMIN_URLS = RULE_ADMIN_URL.split(",")
    for url in RULE_ADMIN_URLS:
        try:
            url = f"{url}/v2/domains/{source}/rules/{rule_name}/{rule_version}"
            print(url)
            headers = {
                "Authorization": f"Bearer {token['access_token']}"
            }

            response = get_request(url, headers=headers)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            continue

    return None


def generate_index_filter(id_key: str, id_value: str):
    """
    Generate an index filter for a given id key and id value.
    """

    if id_key in REQUEST_PAYLOAD_FIELDS:
        return f"requestPayload.{id_key}:{id_value}"
    elif id_key in REQUEST_METADATA_FIELDS:
        return f"requestMetadata.{id_key}:{id_value}"
    else:
        return f"{id_key}:{id_value}"

def calculate_cooloff_period(id_key: str, id_value: str, source: str, time_period: str, amount_limit: Optional[int] = None, count_limit: Optional[int] = None):
    """
    Calculate the cooloff period for a given id key, id value, source, time period in seconds and either amount limit or count limit.
    """

    if amount_limit is None and count_limit is None:
        raise ValueError("Either amount limit or count limit must be provided")

    if amount_limit is not None and count_limit is not None:
        raise ValueError("Only one of amount limit or count limit can be provided")
    
    index_filter = generate_index_filter(id_key, id_value)

    start_time = datetime.utcnow() - timedelta(seconds=int(time_period))
    end_time = datetime.utcnow()

    logs = fetch_logs_timerange(index_filter, start_time.strftime('%Y-%m-%d'), end_time.strftime('%Y-%m-%d'))

    total_amount = 0
    transaction_count = 0
    last_valid_log = None

    for log in logs:
        if amount_limit is not None:
            total_amount += log.get("eventAmount", 0)
            if total_amount > amount_limit:
                break
        elif count_limit is not None:
            transaction_count += 1
            if transaction_count > count_limit:
                break
        last_valid_log = log

    if last_valid_log:
        if isinstance(last_valid_log["@timestamp"], list):
            last_valid_log["@timestamp"] = last_valid_log["@timestamp"][0]
        last_transaction_time = datetime.strptime(last_valid_log["@timestamp"], '%Y-%m-%dT%H:%M:%S.%fZ')
        cooloff_end_time = last_transaction_time + timedelta(seconds=int(time_period))
        return cooloff_end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'