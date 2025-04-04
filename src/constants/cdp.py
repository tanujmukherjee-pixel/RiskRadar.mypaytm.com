import os

PERMITTED_DATASETS = os.environ.get("PERMITTED_DATASETS", "").split(",")
PERMITTED_DATABASES = os.environ.get("PERMITTED_DATABASES", "").split(",")
PERMITTED_TABLES = os.environ.get("PERMITTED_TABLES", "").split(",")