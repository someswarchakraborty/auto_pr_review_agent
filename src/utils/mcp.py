"""MCP (Model Context Protocol) client implementation for GitHub PR reviews."""
from typing import Dict, List, Optional, Any
import aiohttp
import logging
from src.core.models import PRContext, Issue

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for interacting with GitHub through MCP."""

    def __init__(self, base_url: str, github_token: str, github_api_url: str = "https://api.github.com"):
        """Initialize MCP client.
        
        Args:
            base_url: MCP endpoint URL (for GitHub-hosted MCP, use https://mcp.github.dev/v1)
            github_token: GitHub token for authentication
            github_api_url: GitHub API URL (default: https://api.github.com)
        """
        self.base_url = base_url.rstrip('/')
        self.github_api_url = github_api_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {github_token}",  # GitHub API v3 format
            "Accept": "application/vnd.github.v3+json",  # Explicit GitHub API version
            "X-GitHub-Api-Version": "2022-11-28",  # GitHub API version date
            "Content-Type": "application/json"
        }

    async def analyze_pull_request(self, pr_context: PRContext) -> List[Issue]:
        """Analyze a pull request using MCP.
        
        Args:
            pr_context: Context information about the pull request
            
        Returns:
            List of issues found in the PR
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # MCP endpoint for PR analysis
            url = f"{self.base_url}/analyze/pr"
            
            # Prepare PR data for MCP
            pr_data = {
                "repository": pr_context.repository,
                "pull_request": pr_context.pr_number,
                "files": pr_context.files_changed,
                "diff_content": pr_context.diff_content
            }
            
            async with session.post(url, json=pr_data) as response:
                if response.status != 200:
                    raise Exception(f"MCP request failed: {await response.text()}")
                
                result = await response.json()
                return self._convert_mcp_results(result)

    async def get_file_context(self, file_path: str, repository: str) -> Dict[str, Any]:
        """Get file context information through MCP.
        
        Args:
            file_path: Path to the file
            repository: Repository identifier
            
        Returns:
            File context information
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = f"{self.base_url}/context/file"
            
            params = {
                "path": file_path,
                "repository": repository
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"MCP file context request failed: {await response.text()}")
                
                return await response.json()

    def _convert_mcp_results(self, mcp_results: Dict[str, Any]) -> List[Issue]:
        """Convert MCP analysis results to internal Issue format.
        
        Args:
            mcp_results: Results from MCP analysis
            
        Returns:
            List of Issue objects
        """
        issues = []
        for result in mcp_results.get("issues", []):
            issues.append(Issue(
                severity=result.get("severity", "info"),
                message=result.get("message", ""),
                file_path=result.get("file", ""),
                line_number=result.get("line"),
                code_snippet=result.get("code"),
                rule_name=result.get("rule", "mcp_analysis"),
                suggested_fix=result.get("suggestion")
            ))
        return issues

    async def get_pending_reviews(self, repositories: List[str]) -> List[Dict[str, Any]]:
        """Get list of PRs pending review from specified repositories.
        
        Args:
            repositories: List of repository identifiers to check
            
        Returns:
            List of PR information dictionaries
        """
        all_prs = []
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for repo in repositories:
                # Use GitHub's API directly to get pull requests
                url = f"{self.github_api_url}/repos/{repo}/pulls"
                params = {
                    "state": "open",
                    "sort": "updated",
                    "direction": "desc"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 404:
                        logger.warning(f"Repository not found or no access: {repo}")
                        continue
                    elif response.status != 200:
                        text = await response.text()
                        raise Exception(f"Failed to get pending reviews for {repo}: {text}")
                    
                    prs = await response.json()
                    for pr in prs:
                        all_prs.append({
                            "number": pr["number"],
                            "repository": repo,
                            "title": pr["title"],
                            "url": pr["html_url"],
                            "author": pr["user"]["login"],
                            "created_at": pr["created_at"],
                            "updated_at": pr["updated_at"]
                        })
        
        return all_prs

    async def get_pr_context(self, pr_info: Dict[str, Any]) -> PRContext:
        """Get detailed context information for a specific PR.
        
        Args:
            pr_info: Basic PR information from get_pending_reviews
            
        Returns:
            PRContext object with detailed PR information
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Get PR details
            pr_url = f"{self.github_api_url}/repos/{pr_info['repository']}/pulls/{pr_info['number']}"
            async with session.get(pr_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get PR details: {await response.text()}")
                pr_data = await response.json()

            # Get PR files
            files_url = f"{pr_url}/files"
            async with session.get(files_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get PR files: {await response.text()}")
                files_data = await response.json()

            # Build diff content
            diff_content = ""
            files_changed = []
            for file in files_data:
                files_changed.append(file['filename'])
                if file.get('patch'):
                    diff_content += f"diff --git a/{file['filename']} b/{file['filename']}\n"
                    diff_content += file['patch'] + "\n"

            return PRContext(
                pr_number=pr_data["number"],
                repository=pr_info["repository"],
                base_branch=pr_data["base"]["ref"],
                head_branch=pr_data["head"]["ref"],
                files_changed=files_changed,
                diff_content=diff_content,
                author=pr_data["user"]["login"],
                title=pr_data["title"],
                description=pr_data.get("body", "")
            )

    async def post_review(self, repository: str, pr_number: int, review_result: Any) -> None:
        """Post a review to a pull request.
        
        Args:
            repository: Repository identifier
            pr_number: Pull request number
            review_result: Review result to post
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = f"{self.base_url}/pr/{repository}/{pr_number}/review"
            
            review_data = {
                "issues": [issue.dict() for issue in review_result.issues],
                "summary": review_result.summary,
                "stats": review_result.stats
            }
            
            async with session.post(url, json=review_data) as response:
                if response.status != 200:
                    raise Exception(f"Failed to post review: {await response.text()}")

    async def validate_architecture(self, 
                                 file_path: str, 
                                 content: str, 
                                 rules: List[Dict]) -> List[Issue]:
        """Validate architecture rules using MCP.
        
        Args:
            file_path: Path to the file
            content: File content
            rules: Architecture rules to validate
            
        Returns:
            List of architecture issues found
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = f"{self.base_url}/validate/architecture"
            
            data = {
                "file_path": file_path,
                "content": content,
                "rules": rules
            }
            
            async with session.post(url, json=data) as response:
                if response.status != 200:
                    raise Exception(f"MCP architecture validation failed: {await response.text()}")
                
                return self._convert_mcp_results(await response.json())