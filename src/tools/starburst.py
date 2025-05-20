import os
import uuid
import tempfile
import time
import random
from typing import Dict, List, Optional, Tuple, Any, Callable
import pandas as pd
from trino.dbapi import connect
from ..constants.cdp import PERMITTED_DATABASES, PERMITTED_TABLES

async def fetch_table_schema(table_name: str):
    """
    Fetches the schema of a table from the starburst database
    """
    query = f"DESCRIBE {table_name}"
    return await execute_query(query)


async def execute_query(query: str):
    """
    Executes a query on the starburst database
    """

    # if "select" not in query.lower():
    #     raise ValueError("Fetch dataset first and then use fetch_schema_from_dataset_id_tool to get the schema details")


    connection = await _connect()
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()


async def _connect() -> None:
    """Establish a connection to the Trino server."""
    connection = connect(
        host=os.getenv('STARBURST_HOST', 'https://cdp-dashboarding.platform.mypaytm.com'),
        port=443,
        user=os.getenv('STARBURST_USER', 'suyash.pandey@paytm.com'),
        catalog=os.getenv('STARBURST_CATALOG', 'hive'),
        request_timeout=3600
    )
    return connection

async def fetch_permitted_schemas() -> List[str]:
    """
    Fetches the list of permitted schemas from the starburst database
    """
    query = """
    SHOW SCHEMAS
    """

    permitted_schemas = []
    for schema in await execute_query(query):
        if schema[0] in PERMITTED_DATABASES:
            permitted_schemas.append(schema[0])
    return permitted_schemas


async def fetch_permitted_tables(schema: str) -> List[str]:
    """
    Fetches the list of permitted tables from the starburst database
    """
    query = f"""
    SHOW TABLES IN {schema}
    """ 
    permitted_tables = []
    for table in await execute_query(query):
        if table[0] in PERMITTED_TABLES:
            permitted_tables.append(table[0])
    return permitted_tables
