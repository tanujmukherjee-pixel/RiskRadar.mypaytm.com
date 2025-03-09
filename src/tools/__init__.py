from .druid import execute_query_pulse, fetch_all_segments, get_all_funnels, fetch_query, fetch_all_applicable_segments
from .mongo import execute_query_mongo
from ..utils.time import get_current_date
from llama_index.core.tools import FunctionTool
from .cdp import fetch_all_datasets, fetch_dataset_schema
from .starburst import execute_query
from .bitbucket import get_workspace_info, get_repository_info, get_commits, analyze_contributions, get_all_branches, get_all_repositories, call_bitbucket_api

druid_tool = FunctionTool.from_defaults(fn=execute_query_pulse)
segments_tool = FunctionTool.from_defaults(fn=fetch_all_segments)
funnels_tool = FunctionTool.from_defaults(fn=get_all_funnels)
base_query_tool = FunctionTool.from_defaults(fn=fetch_query)
applicable_segments_tool = FunctionTool.from_defaults(fn=fetch_all_applicable_segments)
mongo_tool = FunctionTool.from_defaults(fn=execute_query_mongo)
current_date_tool = FunctionTool.from_defaults(fn=get_current_date)
fetch_all_datasets_tool = FunctionTool.from_defaults(fn=fetch_all_datasets)
fetch_dataset_schema_tool = FunctionTool.from_defaults(fn=fetch_dataset_schema)
current_date_tool = FunctionTool.from_defaults(fn=get_current_date)
execute_query_tool = FunctionTool.from_defaults(fn=execute_query)
get_workspace_info_tool = FunctionTool.from_defaults(fn=get_workspace_info)
get_repository_info_tool = FunctionTool.from_defaults(fn=get_repository_info)
get_commits_tool = FunctionTool.from_defaults(fn=get_commits)
analyze_contributions_tool = FunctionTool.from_defaults(fn=analyze_contributions)
get_all_branches_tool = FunctionTool.from_defaults(fn=get_all_branches)
get_all_repositories_tool = FunctionTool.from_defaults(fn=get_all_repositories)
call_bitbucket_api_tool = FunctionTool.from_defaults(fn=call_bitbucket_api)

tools = {
    "druid_tool": druid_tool,
    "segments_tool": segments_tool,
    "funnels_tool": funnels_tool,
    "base_query_tool": base_query_tool,
    "applicable_segments_tool": applicable_segments_tool,
    "mongo_tool": mongo_tool,
    "current_date_tool": current_date_tool,
    "fetch_all_datasets_tool": fetch_all_datasets_tool,
    "fetch_dataset_schema_tool": fetch_dataset_schema_tool,
    "execute_query_tool": execute_query_tool,
    "get_workspace_info_tool": get_workspace_info_tool,
    "get_repository_info_tool": get_repository_info_tool,
    "get_commits_tool": get_commits_tool,
    "analyze_contributions_tool": analyze_contributions_tool,
    "get_all_branches_tool": get_all_branches_tool,
    "get_all_repositories_tool": get_all_repositories_tool,
    "call_bitbucket_api_tool": call_bitbucket_api_tool
}