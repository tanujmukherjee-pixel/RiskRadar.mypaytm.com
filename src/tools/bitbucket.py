from typing import List, Dict
from src.utils.api import async_get_request
import base64
username="Anshul1Chauhan"
app_password="REDACTED_ATLASSIAN_TOKEN"
workspace="paytmteam"
base_url: str = "https://api.bitbucket.org/2.0"

def _create_auth_header():
    return {
        "Authorization": f"Basic {base64.b64encode(f'{username}:{app_password}'.encode()).decode()}"
    }

async def get_workspace_info() -> Dict:
    """Get workspace information"""
    url = f"{base_url}/workspaces/{workspace}"
    try:
        response = await async_get_request(url, _create_auth_header())
        return response
    except Exception as e:
        return {"error": str(e)}


async def get_repository_info(repo_slug: str) -> Dict:
    """Get repository information"""
    url = f"{base_url}/repositories/{workspace}/{repo_slug}"
    try:
        response = await async_get_request(url, _create_auth_header())
        return response
    except Exception as e:
        return {"error": str(e)}

async def get_all_branches(repo_slug: str) -> List[Dict]:
    """Get all branches from a repository"""
    url = f"{base_url}/repositories/{workspace}/{repo_slug}/refs/branches"
    try:
        response = await async_get_request(url, _create_auth_header())
        return response
    except Exception as e:
        return {"error": str(e)}

async def get_commits(repo_slug: str, branch: str = "main") -> List[Dict]:
    """Get all commits from a branch"""
    commits = []
    url = f"{base_url}/repositories/{workspace}/{repo_slug}/commits/{branch}"
    
    while url:
        try:
            headers = _create_auth_header()
            headers["Content-Type"] = "application/json"
            response = await async_get_request(url, headers)
            commits.extend(response.get("values", []))
            url = response.get("next")
        except Exception as e:
            break
    
    return commits

async def analyze_contributions(repo_slug: str, branch: str) -> Dict:
    """Analyze contributor statistics"""
    commits = await get_commits(repo_slug, branch)
    stats = {
        "total_commits": len(commits),
        "contributors": {},
        "agent_commits": 0,
        "developer_commits": 0
    }
    
    for commit in commits:
        author = commit.get("author", {})
        name = author.get("user", {}).get("display_name", author.get("raw", "Unknown"))
        
        if name not in stats["contributors"]:
            stats["contributors"][name] = {
                "commits": 0,
                "is_agent": "devin" in name.lower(),
                "lines_changed": 0,
                "commit_messages": []
            }
        
        stats["contributors"][name]["commits"] += 1
        stats["contributors"][name]["commit_messages"].append(commit.get("message", ""))
        
        if stats["contributors"][name]["is_agent"]:
            stats["agent_commits"] += 1
        else:
            stats["developer_commits"] += 1
    
    # Calculate percentages
    for name, contributor in stats["contributors"].items():
        contributor["percentage"] = (contributor["commits"] / stats["total_commits"]) * 100 if stats["total_commits"] > 0 else 0
    
    return stats


async def get_all_repositories(page: int = 1) -> List[Dict]:
    """Get all repositories"""
    url = f"{base_url}/repositories/{workspace}?page={page}&sort=-updated_on"
    try:
        response = await async_get_request(url, _create_auth_header())
        return response
    except Exception as e:
        return {"error": str(e)}
    
async def call_bitbucket_api(url: str) -> Dict:
    """Call the Bitbucket API"""
    try:
        response = await async_get_request(url, _create_auth_header())
        return response
    except Exception as e:
        return {"error": str(e)}