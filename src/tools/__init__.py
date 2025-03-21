from .druid import execute_query_pulse, fetch_all_segments, get_all_funnels, fetch_query, fetch_all_applicable_segments, fetch_insight_details, fetch_all_insights
from .mongo import execute_query_mongo
from ..utils.time import get_current_date
from llama_index.core.tools import FunctionTool
from .cdp import fetch_all_datasets, fetch_schema_name_from_dataset_id
from .starburst import execute_query, fetch_permitted_schemas, fetch_permitted_tables
from .bitbucket import get_workspace_info, get_repository_info, get_commits, analyze_contributions, get_all_branches, get_all_repositories, call_bitbucket_api
from .self_heal import drain_node, cordon_node, uncordon_node, get_dns_hostname, clean_up_node, get_node, install_awscli, get_node_instance_id

druid_tool = FunctionTool.from_defaults(fn=execute_query_pulse)
segments_tool = FunctionTool.from_defaults(fn=fetch_all_segments)
funnels_tool = FunctionTool.from_defaults(fn=get_all_funnels)
base_query_tool = FunctionTool.from_defaults(fn=fetch_query)
applicable_segments_tool = FunctionTool.from_defaults(fn=fetch_all_applicable_segments)
mongo_tool = FunctionTool.from_defaults(fn=execute_query_mongo)
current_date_tool = FunctionTool.from_defaults(fn=get_current_date)
fetch_all_datasets_tool = FunctionTool.from_defaults(fn=fetch_all_datasets)
fetch_schema_name_from_dataset_id_tool = FunctionTool.from_defaults(fn=fetch_schema_name_from_dataset_id)
current_date_tool = FunctionTool.from_defaults(fn=get_current_date)
execute_query_tool = FunctionTool.from_defaults(fn=execute_query)
get_workspace_info_tool = FunctionTool.from_defaults(fn=get_workspace_info)
get_repository_info_tool = FunctionTool.from_defaults(fn=get_repository_info)
get_commits_tool = FunctionTool.from_defaults(fn=get_commits)
analyze_contributions_tool = FunctionTool.from_defaults(fn=analyze_contributions)
get_all_branches_tool = FunctionTool.from_defaults(fn=get_all_branches)
get_all_repositories_tool = FunctionTool.from_defaults(fn=get_all_repositories)
call_bitbucket_api_tool = FunctionTool.from_defaults(fn=call_bitbucket_api)
fetch_permitted_schemas_tool = FunctionTool.from_defaults(fn=fetch_permitted_schemas)
fetch_permitted_tables_tool = FunctionTool.from_defaults(fn=fetch_permitted_tables)
fetch_all_insights_tool = FunctionTool.from_defaults(fn=fetch_all_insights)
fetch_insight_details_tool = FunctionTool.from_defaults(fn=fetch_insight_details)
drain_node_tool = FunctionTool.from_defaults(fn=drain_node)
cordon_node_tool = FunctionTool.from_defaults(fn=cordon_node)
uncordon_node_tool = FunctionTool.from_defaults(fn=uncordon_node)
get_dns_hostname_tool = FunctionTool.from_defaults(fn=get_dns_hostname)
clean_up_node_tool = FunctionTool.from_defaults(fn=clean_up_node)
get_node_tool = FunctionTool.from_defaults(fn=get_node)
install_awscli_tool = FunctionTool.from_defaults(fn=install_awscli)
get_node_instance_id_tool = FunctionTool.from_defaults(fn=get_node_instance_id)

tools = {
    "druid_tool": druid_tool,
    "segments_tool": segments_tool,
    "funnels_tool": funnels_tool,
    "base_query_tool": base_query_tool,
    "applicable_segments_tool": applicable_segments_tool,
    "mongo_tool": mongo_tool,
    "current_date_tool": current_date_tool,
    "fetch_all_datasets_tool": fetch_all_datasets_tool,
    "fetch_schema_name_from_dataset_id_tool": fetch_schema_name_from_dataset_id_tool,
    "execute_query_tool": execute_query_tool,
    "get_workspace_info_tool": get_workspace_info_tool,
    "get_repository_info_tool": get_repository_info_tool,
    "get_commits_tool": get_commits_tool,
    "analyze_contributions_tool": analyze_contributions_tool,
    "get_all_branches_tool": get_all_branches_tool,
    "get_all_repositories_tool": get_all_repositories_tool,
    "call_bitbucket_api_tool": call_bitbucket_api_tool,
    "fetch_permitted_schemas_tool": fetch_permitted_schemas_tool,
    "fetch_permitted_tables_tool": fetch_permitted_tables_tool,
    "fetch_all_insights_tool": fetch_all_insights_tool,
    "fetch_insight_details_tool": fetch_insight_details_tool,
    "drain_node": drain_node_tool,
    "cordon_node": cordon_node_tool,
    "uncordon_node": uncordon_node_tool,
    "get_dns_hostname": get_dns_hostname_tool,
    "clean_up_node": clean_up_node_tool,
    "get_node": get_node_tool,
    "install_awscli": install_awscli_tool,
    "get_node_instance_id": get_node_instance_id_tool
}