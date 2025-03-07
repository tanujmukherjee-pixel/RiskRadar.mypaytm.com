from ..base import BaseAgent
from llama_index.core.tools import FunctionTool
from ...tools.bitbucket import get_workspace_info, get_repository_info, get_commits, analyze_contributions, get_all_branches, get_all_repositories

class BitbucketAgent(BaseAgent):
    def __init__(self):
        super().__init__("bitbucket",[])
        self.tools = self.get_tools()
    
    def get_tools(self):
        get_workspace_info_tool = FunctionTool.from_defaults(fn=get_workspace_info)
        get_repository_info_tool = FunctionTool.from_defaults(fn=get_repository_info)
        get_commits_tool = FunctionTool.from_defaults(fn=get_commits)
        analyze_contributions_tool = FunctionTool.from_defaults(fn=analyze_contributions)
        get_all_branches_tool = FunctionTool.from_defaults(fn=get_all_branches)
        get_all_repositories_tool = FunctionTool.from_defaults(fn=get_all_repositories)
        return [get_workspace_info_tool, get_repository_info_tool, get_commits_tool, analyze_contributions_tool, get_all_branches_tool, get_all_repositories_tool]