# environment contract

- all required configuration keys must be listed in an example file.
  - example env file path: `.env` (gitignored — never commit; create locally from the table below)
- local dev must not require production secrets.
- if the system depends on external services (db, cache, queues, etc.), provide one of:
  - a single command that starts dependencies locally (containerized or otherwise), or
  - clear setup instructions in the runbook.

| variable | required | description | example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | yes | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/agency` |
| `ELASTICSEARCH_HOST` | yes | Elasticsearch base URL | `https://es.internal.example.com:443` |
| `RULE_ADMIN_HOST` | yes | Rule admin service base URL | `https://rule-admin.internal.example.com` |
| `RULE_ADMIN_TOKEN` | yes | Bearer token for rule admin API | `ya29.a0...` |
| `DEFAULT_SERVICE_ACCOUNT_FILE` | yes | Path to Google service account JSON | `data/agents/rc-lookup/service-account.json` |
| `DEFAULT_USER_EMAIL` | yes | Google service account email | `svc@project.iam.gserviceaccount.com` |
| `GOOGLE_SCOPES` | no | Comma-separated Google OAuth scopes | `https://www.googleapis.com/auth/userinfo.email` |
| `ENABLE_ALL_ACCESS` | no | If `true`, disables CDP dataset/table restrictions | `false` |
| `PERMITTED_DATASETS` | no | Comma-separated CDP datasets the agent may query | `dataset1,dataset2` |
| `PERMITTED_DATABASES` | no | Comma-separated databases the agent may query | `db1,db2` |
| `PERMITTED_TABLES` | no | Comma-separated tables the agent may query | `table1,table2` |
| `REQUEST_PAYLOAD_FIELDS` | no | Kibana request payload fields to extract | `paytmUserId,paytmMerchantId,eventAmount` |
| `REQUEST_METADATA_FIELDS` | no | Kibana metadata fields to extract | `customerId` |
| `BASE_FIELDS` | no | Kibana base fields to include in responses | `actionRecommended,@timestamp` |

## rules

- never hardcode secrets. never commit `.env`.
- if a required env var is missing, fail loudly -- do not silently default.
