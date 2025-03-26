from ..repositories.audit_logs_repository import AuditLogsRepository
from ..constants.database import ELASTICSEARCH_HOST

def fetch_logs(id, delta_time=3600):
    """
    Fetch logs from Kibana (Elasticsearch) based on an id and delta time in seconds.
    """
    repository = AuditLogsRepository(elasticsearch_host=ELASTICSEARCH_HOST)
    logs = list(repository.search_audit_logs(id, delta_time))
    return logs

def fetch_all_logs(delta_time=3600):
    """
    Fetch all logs from Kibana (Elasticsearch) based on delta time in seconds.
    """
    repository = AuditLogsRepository(elasticsearch_host=ELASTICSEARCH_HOST)
    logs = repository.search_audit_logs("*", delta_time)
    return logs
