# Logging Standards

- always use a single logger class/module to do logging
- put logs in the logs/ folder
- organize logs by their filenames that include the timestamp. make it easy to find out the logs for any session.
- always have latest.log point to the last running session's log file.
- rotate logs if the files bloat up and reach 50% of the disk space - unless specifically needed by the repo. 
- in general, do not put user pii data into log files
- always have a debug flag, which when set will log a lot of data. this will help identify errors in code and help solve them quickly. turn off debug flag once the error has been found and fixed.

## Log Levels

| Level | When to use |
|-------|------------|
| `ERROR` | Exceptions, connector execution failures, 5xx responses |
| `WARN` | Recoverable issues, 4xx responses, degraded state |
| `INFO` | Request lifecycle, connector route loading, startup events |
| `DEBUG` | Detailed processing steps, payload details (local only) |

