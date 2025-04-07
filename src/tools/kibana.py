from ..repositories.audit_logs_repository import AuditLogsRepository
from ..constants.database import ELASTICSEARCH_HOST

from datetime import datetime, timedelta

def fetch_logs_timerange(id, start_time=None, end_time=None):
    """
    Fetch logs from Kibana (Elasticsearch) based on an id and start and end time.
    """
    if end_time is None:
        end_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    if start_time is None:
        start_time = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
    
    repository = AuditLogsRepository(elasticsearch_host=ELASTICSEARCH_HOST)
    logs = list(repository.search_audit_logs_timerange(id, start_time, end_time))
    return logs


def fetch_all_logs(delta_time=3600):
    """
    Fetch all logs from Kibana (Elasticsearch) based on delta time in seconds.
    """
    repository = AuditLogsRepository(elasticsearch_host=ELASTICSEARCH_HOST)
    logs = repository.search_audit_logs("*", delta_time)
    return logs