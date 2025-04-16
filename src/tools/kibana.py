from ..repositories.audit_logs_repository import AuditLogsRepository
from ..constants.database import ELASTICSEARCH_HOST

from datetime import datetime, timedelta

def fetch_logs_timerange(id, start_time=None, end_time=None):
    """
    Fetch logs from Kibana (Elasticsearch) based on an id and start and end time.
    """
    if end_time is None:
        end_time = datetime.utcnow().strftime('%Y-%m-%d')
    if start_time is None:
        start_time = (datetime.utcnow() - timedelta(days=0)).strftime('%Y-%m-%d')

    # Convert various date formats to YYYY-MM-DD
    try:
        # Try parsing with various common formats including datetime format
        for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y']:
            try:
                start_time = datetime.strptime(start_time, fmt).strftime('%Y-%m-%d')
                break
            except ValueError:
                continue
        
        for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y']:
            try:
                end_time = datetime.strptime(end_time, fmt).strftime('%Y-%m-%d')
                break
            except ValueError:
                continue
                
    except Exception as e:
        raise ValueError(f"Unable to parse date strings. Please use format YYYY-MM-DD: {str(e)}")
    
    print(f"{start_time} {end_time}")

    repository = AuditLogsRepository(elasticsearch_host=ELASTICSEARCH_HOST)
    logs = list(repository.search_audit_logs_timerange(f"{id}", start_time, end_time))
    return logs


def fetch_all_logs(delta_time=3600):
    """
    Fetch all logs from Kibana (Elasticsearch) based on delta time in seconds.
    """
    repository = AuditLogsRepository(elasticsearch_host=ELASTICSEARCH_HOST)
    logs = repository.search_audit_logs("*", delta_time)
    return logs