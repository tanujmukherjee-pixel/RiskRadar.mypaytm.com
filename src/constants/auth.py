import os

DEFAULT_SERVICE_ACCOUNT_FILE = os.environ.get("DEFAULT_SERVICE_ACCOUNT_FILE", "data/agents/rc-lookup/rule-admin-b9e4c17a37da.json")
DEFAULT_USER_EMAIL = os.environ.get("DEFAULT_USER_EMAIL", "rc-lookup@rule-admin.iam.gserviceaccount.com")
GOOGLE_SCOPES = os.environ.get("GOOGLE_SCOPES", "https://www.googleapis.com/auth/userinfo.email").split(",")