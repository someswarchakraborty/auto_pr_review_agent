"""GitHub utilities for the PR Reviewer Agent."""
from typing import Dict, List, Optional
import aiohttp
from ..core.models import PRContext

async def fetch_pr_details(
    repo: str,
    pr_number: int,
    github_token: str
) -> PRContext:
    """Fetch pull request details from GitHub.

    Args:
        repo: Repository name in format 'owner/repo'
        pr_number: Pull request number
        github_token: GitHub authentication token

    Returns:
        PRContext object with PR details
    """
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        # Fetch PR metadata
        pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
        async with session.get(pr_url) as response:
            pr_data = await response.json()
        
        # Fetch PR files
        files_url = f"{pr_url}/files"
        async with session.get(files_url) as response:
            files_data = await response.json()

        return PRContext(
            pr_number=pr_number,
            repository=repo,
            base_branch=pr_data["base"]["ref"],
            head_branch=pr_data["head"]["ref"],
            files_changed=[f["filename"] for f in files_data],
            diff_content={
                f["filename"]: await fetch_file_content(session, repo, f["raw_url"])
                for f in files_data
            },
            author=pr_data["user"]["login"],
            title=pr_data["title"],
            description=pr_data["body"]
        )

async def fetch_file_content(
    session: aiohttp.ClientSession,
    repo: str,
    raw_url: str
) -> str:
    """Fetch file content from GitHub.

    Args:
        session: aiohttp ClientSession
        repo: Repository name
        raw_url: URL to raw file content

    Returns:
        File content as string
    """
    async with session.get(raw_url) as response:
        return await response.text()

async def post_review_comment(
    repo: str,
    pr_number: int,
    github_token: str,
    body: str,
    commit_id: Optional[str] = None,
    path: Optional[str] = None,
    line: Optional[int] = None
) -> None:
    """Post a review comment on a pull request.

    Args:
        repo: Repository name in format 'owner/repo'
        pr_number: Pull request number
        github_token: GitHub authentication token
        body: Comment content
        commit_id: Optional commit SHA
        path: Optional file path for line comments
        line: Optional line number for line comments
    """
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    
    # Prepare review comments
    comments = []
    if path and line:
        comments.append({
            "path": path,
            "line": line,
            "body": body
        })
    
    review_data = {
        "body": body if not (path and line) else None,
        "event": "COMMENT",
        "comments": comments
    }
    
    if commit_id:
        review_data["commit_id"] = commit_id
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, json=review_data) as response:
            if response.status not in (200, 201):
                response_data = await response.json()
                raise Exception(f"Failed to post review: {response_data}")