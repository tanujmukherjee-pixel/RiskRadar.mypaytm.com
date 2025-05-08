import boto3
import os

S3_PROFILE =  os.getenv('S3_PROFILE', "PaiRiskDataScienceDevOps")
ENABLE_PROFILE = os.getenv('ENABLE_PROFILE', 'false').lower() == 'true'
CST_EVAL_BUCKET = os.getenv('CST_EVAL_BUCKET', "agency-stg")


async def fetch_docs_from_s3(agent_name: str, output_path: str):
    """Fetch docs from s3 and save to disk."""
    try:
        print(f"Fetching docs from s3: {agent_name}")
        # Initialize S3 client
        if ENABLE_PROFILE:
            session = boto3.Session(profile_name=S3_PROFILE)
        else:
            session = boto3.Session()
        s3_client = session.client('s3')
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # List and download all files in the agent's directory
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=CST_EVAL_BUCKET, Prefix=f"{agent_name}/"):
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    # Skip the directory itself
                    if key.endswith('/'):
                        continue
                    # Create local path matching S3 structure
                    local_path = os.path.join(os.path.dirname(output_path), key)
                    # Ensure parent directory exists
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    # Download the file
                    s3_client.download_file(CST_EVAL_BUCKET, key, local_path)
    except Exception as e:
        logger.error(f"Error fetching docs from s3: {e}")
        raise e