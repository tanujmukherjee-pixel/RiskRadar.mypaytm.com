import os
import logging
from src.utils.s3 import fetch_docs_from_s3, CST_EVAL_BUCKET, ENABLE_PROFILE, S3_PROFILE
import boto3
from ..constants.path import DOCS_PATH

logger = logging.getLogger(__name__)

def fetch_all_docs():
    """Fetch all agent docs from s3."""
    try:
        # Initialize S3 client
        if ENABLE_PROFILE:
            session = boto3.Session(profile_name=S3_PROFILE)
        else:
            session = boto3.Session()
        s3_client = session.client('s3')

        # List all agent folders (prefixes)
        paginator = s3_client.get_paginator('list_objects_v2')
        agent_folders = set()
        for page in paginator.paginate(Bucket=CST_EVAL_BUCKET, Delimiter='/'):
            if 'CommonPrefixes' in page:
                for prefix in page['CommonPrefixes']:
                    folder = prefix['Prefix'].rstrip('/')
                    agent_folders.add(folder)
        
        logger.info(f"Found agent folders: {agent_folders}")
        
        # Fetch docs for each agent
        for agent_name in agent_folders:
            output_path = os.path.join(f"{DOCS_PATH.format(agent_name=agent_name)}/")
            try:
                # fetch_docs_from_s3 is async, so run it in event loop if needed
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(fetch_docs_from_s3(agent_name, output_path))
                else:
                    loop.run_until_complete(fetch_docs_from_s3(agent_name, output_path))
            except Exception as e:
                logger.error(f"Error fetching docs for agent {agent_name}: {e}")
    except Exception as e:
        logger.error(f"Error listing agent folders in s3: {e}")

def fetch_docs_for_agent(agent_name: str, output_base_path='docs'):
    """Fetch docs for an agent from s3."""
    try:
        output_path = os.path.join(output_base_path, agent_name)
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(fetch_docs_from_s3(agent_name, output_path))
        else:
            loop.run_until_complete(fetch_docs_from_s3(agent_name, output_path))
    except Exception as e:
        logger.error(f"Error fetching docs for agent {agent_name}: {e}")