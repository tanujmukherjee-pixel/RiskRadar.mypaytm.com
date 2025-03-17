import os
import uuid
import tempfile
import time
import random
from typing import Dict, List, Optional, Tuple, Any, Callable

import pandas as pd
from trino.dbapi import connect
from trino.exceptions import TrinoQueryError

def execute_query(query: str):
    """
    Executes a query on the starburst database
    """
    connection = _connect()
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()


def _connect() -> None:
    """Establish a connection to the Trino server."""
    connection = connect(
        host=os.getenv('STARBURST_HOST', 'https://cdp-dashboarding.platform.mypaytm.com'),
        port=443,
        user=os.getenv('STARBURST_USER', 'mujeebul.ansari@paytm.com'),
        catalog=os.getenv('STARBURST_CATALOG', 'hive'),
        request_timeout=3600
    )
    return connection

def fetch_permitted_schemas() -> List[str]:
    """
    Fetches the list of permitted schemas from the starburst database
    """
    query = """
    SHOW SCHEMAS
    """
    return execute_query(query)


def fetch_permitted_tables(schema: str) -> List[str]:
    """
    Fetches the list of permitted tables from the starburst database
    """
    query = f"""
    SHOW TABLES IN {schema}
    """ 
    return execute_query(query)