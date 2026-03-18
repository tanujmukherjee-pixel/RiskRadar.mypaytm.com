import base64
from typing import Dict, List, Optional, Union

from src.utils.api import get_request

username = "Anshul1Chauhan"
app_password = "REDACTED_ATLASSIAN_TOKEN"
workspace = "paytmteam"
base_url: str = "https://api.bitbucket.org/2.0"


def _create_auth_header():
    return {
        "Authorization": f"Basic {base64.b64encode(f'{username}:{app_password}'.encode()).decode()}"
    }


def get_workspace_info() -> Dict:
    """Get workspace information"""
    url = f"{base_url}/workspaces/{workspace}"
    try:
        response = get_request(url, _create_auth_header())
        return response
    except Exception as e:
        return {"error": str(e)}


def get_repository_info(repo_slug: str) -> Dict:
    """Get repository information"""
    url = f"{base_url}/repositories/{workspace}/{repo_slug}"
    try:
        response = get_request(url, _create_auth_header())
        return response
    except Exception as e:
        return {"error": str(e)}


def get_all_branches(repo_slug: str) -> Union[List[Dict], Dict]:
    """Get all branches from a repository"""
    url = f"{base_url}/repositories/{workspace}/{repo_slug}/refs/branches"
    try:
        response = get_request(url, _create_auth_header())
        return response
    except Exception as e:
        return {"error": str(e)}


def get_commits(repo_slug: str, branch: str = "main") -> List[Dict]:
    """Get all commits from a branch"""
    commits = []
    url: Optional[str] = (
        f"{base_url}/repositories/{workspace}/{repo_slug}/commits/{branch}"
    )

    while url:
        try:
            headers = _create_auth_header()
            headers["Content-Type"] = "application/json"
            response = get_request(url, headers)
            commits.extend(response.get("values", []))
            url = response.get("next")
        except Exception:
            break

    return commits


def get_all_repositories(page: int = 1) -> Union[List[Dict], Dict]:
    """Get all repositories"""
    url = f"{base_url}/repositories/{workspace}?page={page}&sort=-updated_on"
    try:
        response = get_request(url, _create_auth_header())
        return response
    except Exception as e:
        return {"error": str(e)}
