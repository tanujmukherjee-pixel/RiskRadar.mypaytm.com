from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from datetime import datetime, timedelta
from ..constants.kibana import REQUEST_PAYLOAD_FIELDS, REQUEST_METADATA_FIELDS, BASE_FIELDS

class AuditLogsRepository:
    def __init__(self, elasticsearch_host: str, index_pattern: str = "maquette.fraudcheck.audit*"):
        """
        Initialize the repository with Elasticsearch connection details.

        :param elasticsearch_host: The Elasticsearch host URL.
        :param index_pattern: The index pattern to search.
        """
        self.elasticsearch_client = Elasticsearch([elasticsearch_host])
        self.index_pattern = index_pattern

    def search_audit_logs_timerange(self, lucene_query: str, start_time: str, end_time: str, page_size: int = 500, timeout: int = 300):
        """
        Search audit logs using a Lucene query and filter by the last delta_time seconds.

        :param lucene_query: The Lucene query string.
        :param page_size: The number of logs to fetch per page.
        :param timeout: The timeout for the search request in seconds.
        :param start_time: The start time for the search. format: YYYY-MM-DD
        :param end_time: The end time for the search. format: YYYY-MM-DD
        """
        audit_logs = []
        try:
            # Convert start and end times to Elasticsearch format
            start_time = datetime.strptime(start_time + "T00:00:00", '%Y-%m-%dT%H:%M:%S')
            end_time = datetime.strptime(end_time + "T23:59:59", '%Y-%m-%dT%H:%M:%S')

            # Create a search instance
            s = Search(using=self.elasticsearch_client, index=self.index_pattern)

            # Configure the search with the provided request structure
            s = s.extra(
                track_total_hits=False,
                version=True,
                _source=True  # Changed to True to get all fields
            )

            # Configure sorting
            s = s.sort({"dateInserted": {"order": "desc", "unmapped_type": "boolean"}})

            # Configure fields
            s = s.extra(
                fields=[
                    {"field": "*", "include_unmapped": "true"},
                    {"field": "@timestamp", "format": "strict_date_optional_time"},
                    {"field": "actions.configData.threshold_date", "format": "strict_date_optional_time"},
                    {"field": "dateInserted", "format": "strict_date_optional_time"},
                    {"field": "requestPayload.oeMetaData.kycDetails.dateOfBirth", "format": "strict_date_optional_time"},
                    {"field": "requestPayload.oeMetaData.kycDetails.dateOfIncorporation", "format": "strict_date_optional_time"},
                    {"field": "requestPayload.updatedAt", "format": "strict_date_optional_time"}
                ],
                stored_fields=["*"]
            )

            # Configure highlight
            s = s.highlight(
                "*",
                pre_tags=["@kibana-highlighted-field@"],
                post_tags=["@/kibana-highlighted-field@"],
                fragment_size=2147483647
            )

            # Build the bool query
            bool_query = {
                "bool": {
                    "must": [],
                    "filter": [
                        {
                            "bool": {
                                "filter": [
                                    {
                                        "bool": {
                                            "should": [
                                                {"match": {"actionRecommended": "BLOCK"}}
                                            ],
                                            "minimum_should_match": 1
                                        }
                                    },
                                    {
                                        "multi_match": {
                                            "type": "best_fields",
                                            "query": lucene_query,
                                            "lenient": True
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "range": {
                                "dateInserted": {
                                    "format": "strict_date_optional_time",
                                    "gte": start_time,
                                    "lte": end_time
                                }
                            }
                        }
                    ],
                    "should": [],
                    "must_not": []
                }
            }

            # Apply the query
            s = s.query(bool_query)

            # Configure pagination
            s = s.extra(size=page_size)

            # Execute the search and parse the response
            response = s.params(request_timeout=timeout).execute()

            # Parse response and add logs to the result
            for hit in response:
                audit_logs.append(hit.to_dict())

        except Exception as e:
            error = f"Error executing Lucene query '{lucene_query}': {e}"
            return error

        return self.trim(audit_logs)

    def trim(self, audit_logs):
        """
        Trim the audit logs to retain only the specified fields.

        :param audit_logs: List of audit log dictionaries to be trimmed.
        :return: List of trimmed audit logs with only the specified fields.
        """
        
        fields_to_keep = BASE_FIELDS.split(",") + REQUEST_PAYLOAD_FIELDS.split(",") + REQUEST_METADATA_FIELDS.split(",")

        # Iterate over the audit logs and keep only the specified fields
        trimmed_logs = []
        for log in audit_logs:
            def get_nested_value(d, keys):
                for key in keys:
                    if isinstance(d, dict):
                        d = d.get(key)
                    else:
                        return None
                return d

            base_trimmed_log = {field: get_nested_value(log, field.split('.')) for field in fields_to_keep}
            request_payload_trimmed_log = {field: get_nested_value(log.get("requestPayload", {}), field.split('.')) for field in REQUEST_PAYLOAD_FIELDS.split(",")}
            request_metadata_trimmed_log = {field: get_nested_value(log.get("requestMetadata", {}), field.split('.')) for field in REQUEST_METADATA_FIELDS.split(",")}
            # Extract the 'action' array and keep only the first object if it exists
            action_trimmed_log = {}
            action_array = log.get("actions", [])
            if action_array:
                action_trimmed_log["rule_result"] = action_array[0]
            trimmed_logs.append({**base_trimmed_log, **request_payload_trimmed_log, **request_metadata_trimmed_log})

        return trimmed_logs

