import os

RULE_ADMIN_URL = os.environ.get("RULE_ADMIN_HOST", "https://maquette-admin.internal.ap-south-1.production.osmose.risk.pai.mypaytm.com")
RULE_ADMIN_TOKEN = os.environ.get("RULE_ADMIN_TOKEN", "REDACTED_GOOGLE_OAUTH_TOKEN")
