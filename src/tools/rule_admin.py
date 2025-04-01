from ..utils.api import get_request
from ..constants.rule_admin import RULE_ADMIN_URL, RULE_ADMIN_TOKEN

def fetch_rule_info(rule_name: str, rule_version: str, source: str):
    """
    Fetch rule info from the rule admin service using the rule name, rule version and source.
    """

    url = f"{RULE_ADMIN_URL}/v2/domains/{source}/rules/{rule_name}/{rule_version}"
    headers = {
        "Authorization": f"Bearer {RULE_ADMIN_TOKEN}"
    }

    print(url)
    print(headers)

    response = get_request(url, headers=headers)

    return response

