import os

ENABLE_ALL_ACCESS = os.environ.get("ENABLE_ALL_ACCESS", "false").lower() == "true"
PERMITTED_DATASETS = os.environ.get("PERMITTED_DATASETS", "").split(",")
PERMITTED_DATABASES = os.environ.get("PERMITTED_DATABASES", "").split(",")
PERMITTED_TABLES = os.environ.get("PERMITTED_TABLES", "").split(",")