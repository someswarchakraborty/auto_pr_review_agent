# GitHub Integration Guide

## Overview

The PR Reviewer Agent uses GitHub's REST API and webhook system to interact with repositories and perform intelligent code reviews. This integration enables real-time monitoring of pull requests, automated code analysis, and direct feedback through PR comments.

## Integration Methods

### 1. GitHub REST API
- Direct access to repository content
- Pull request management
- Comment and review submissions
- Repository and user information

### 2. Webhooks
- Real-time event notifications
- Secure payload delivery
- Event filtering
- Automatic retries

## Configuration

### Environment Variables

```env
# GitHub Configuration
GITHUB_TOKEN=your_personal_access_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret
REPOSITORY_LIST=owner1/repo1,owner2/repo2

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Configuration File (settings.yaml)

```yaml
github:
  api_version: "2022-11-28"
  webhook_events:
    - pull_request
    - pull_request_review
  max_comments_per_review: 50
  retry_config:
    max_attempts: 3
    initial_delay: 1
    max_delay: 60

integrations:
  github:
    webhook_secret: ${GITHUB_WEBHOOK_SECRET}
    webhook_events:
      - pull_request
      - pull_request_review
    repositories: ${REPOSITORY_LIST}

agent:
  concurrent_reviews: 5
  review_timeout: 300
  max_files_per_review: 100
```

## Integration Features

### 1. Webhook Integration

The agent receives real-time notifications through GitHub webhooks:

```python
@app.post("/webhook")
async def github_webhook(request: Request):
    """Handle GitHub webhook events."""
    try:
        # Verify webhook signature
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256")
        verify_webhook_signature(signature, body, webhook_secret)
        
        # Process the event
        event_type = request.headers.get("X-GitHub-Event")
        event_data = json.loads(body)
        await process_github_event(event_type, event_data)
        
        return {"status": "processing"}
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. GitHub API Integration

The agent uses GitHub's REST API for repository interactions:

```python
class GitHubClient:
    """GitHub API client with retry and rate limit handling."""
    
    async def get_pull_request(self, repo: str, pr_number: int) -> dict:
        """Get PR details with automatic retry and rate limit handling."""
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}"
        return await self._make_request("GET", url)
    
    async def post_review_comment(self, repo: str, pr_number: int, 
                                comment: str, path: str = None, 
                                line: int = None) -> dict:
        """Post a review comment with file location context."""
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}/reviews"
        body = {
            "body": comment,
            "event": "COMMENT",
            "comments": [{"path": path, "line": line, "body": comment}]
                if path and line else []
        }
        return await self._make_request("POST", url, json=body)
```

### 3. Event Processing Pipeline

The agent processes GitHub events through an analysis pipeline:

```python
class PRReviewerAgent:
    """Core agent for processing PR events and coordinating analysis."""
    
    async def handle_github_event(self, event_type: str, 
                                event_data: dict) -> None:
        """Process GitHub webhook events."""
        if event_type == "pull_request":
            await self.process_pull_request(event_data)
        elif event_type == "pull_request_review":
            await self.process_review_feedback(event_data)
    
    async def process_pull_request(self, event_data: dict) -> None:
        """Analyze PR and provide feedback."""
        # Extract PR details
        pr_number = event_data["pull_request"]["number"]
        repo = event_data["repository"]["full_name"]
        
        # Run analysis pipeline
        analysis_results = await self.analyze_pr(repo, pr_number)
        
        # Post review comments
        await self.post_review(repo, pr_number, analysis_results)
```

## Setup and Configuration

### 1. GitHub Setup

1. Create Personal Access Token:
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Generate new token with required scopes:
     - `repo` (full control of private repositories)
     - `workflow` (if using GitHub Actions)

2. Configure Webhook:
   ```bash
   # Start the tunnel for local development
   python scripts/setup_tunnel.py

   # Follow the printed instructions to:
   # 1. Copy the webhook URL
   # 2. Configure in GitHub repository settings
   # 3. Set the webhook secret
   # 4. Select events to monitor
   ```

### 2. Local Development Setup

1. Configure environment:
   ```bash
   # Create and populate .env file
   cp example.env .env
   
   # Add your GitHub token and webhook secret
   echo "GITHUB_TOKEN=your_token_here" >> .env
   echo "GITHUB_WEBHOOK_SECRET=your_secret_here" >> .env
   ```

2. Start the application:
   ```bash
   # Start the FastAPI server
   python src/main.py
   ```

### 3. Using the GitHub Client

The agent provides a `GitHubClient` class for API interactions:

```python
from utils.github import GitHubClient

# Initialize client
client = GitHubClient(
    token=config.github_token,
    base_url="https://api.github.com"
)

# Use GitHub API features
await client.get_pull_request(repo, pr_number)
await client.get_pr_files(repo, pr_number)
await client.post_review(repo, pr_number, comments)
```

## GitHub API Integration

### 1. Webhook Event Processing

The agent receives and processes GitHub webhook events:

```json
{
  "event": "pull_request",
  "action": "opened",
  "pull_request": {
    "number": 123,
    "title": "Feature: Add new security checks",
    "body": "Implements additional security analysis...",
    "head": {
      "ref": "feature/security-updates",
      "sha": "abc123..."
    }
  },
  "repository": {
    "full_name": "owner/repo"
  }
}
```

### 2. PR Analysis Pipeline

The analysis results are structured as:

```json
{
  "summary": {
    "total_files": 5,
    "issues_found": 3,
    "analysis_duration": 2.5
  },
  "issues": [
    {
      "severity": "high",
      "category": "security",
      "message": "SQL injection vulnerability detected",
      "file": "src/handlers/user.py",
      "line": 45,
      "recommendation": "Use parameterized queries"
    }
  ]
}
```

## Error Handling and Recovery

### 1. GitHub API Errors

Handle common API errors:

```python
class GitHubClient:
    async def _make_request(self, method: str, url: str, **kwargs) -> dict:
        """Make GitHub API request with retry and error handling."""
        for attempt in range(self.max_retries):
            try:
                async with self.session.request(method, url, **kwargs) as resp:
                    if resp.status == 429:  # Rate limit
                        reset_time = int(resp.headers['X-RateLimit-Reset'])
                        await self._handle_rate_limit(reset_time)
                        continue
                        
                    resp.raise_for_status()
                    return await resp.json()
                    
            except aiohttp.ClientError as e:
                if attempt == self.max_retries - 1:
                    raise GitHubAPIError(f"API request failed: {e}")
                await asyncio.sleep(self._get_retry_delay(attempt))
```

### 2. Webhook Processing

Robust webhook handling:

```python
async def process_github_event(event_type: str, event_data: dict) -> None:
    """Process GitHub webhook events with error handling."""
    try:
        # Validate event data
        if not self._validate_event_data(event_type, event_data):
            logger.error(f"Invalid event data for type: {event_type}")
            return

        # Process based on event type
        handlers = {
            "pull_request": self._handle_pr_event,
            "pull_request_review": self._handle_review_event
        }
        
        handler = handlers.get(event_type)
        if handler:
            await handler(event_data)
        else:
            logger.warning(f"Unhandled event type: {event_type}")
            
    except Exception as e:
        logger.error(f"Event processing error: {e}", exc_info=True)
        # Could implement retry logic here if needed
```

## Best Practices

### 1. API Usage
- Use conditional requests with ETags
- Implement rate limit monitoring
- Cache responses when appropriate
- Use GraphQL for complex queries

### 2. Webhook Management
- Verify all webhook signatures
- Process events asynchronously
- Implement retry mechanisms
- Monitor webhook deliveries

### 3. Security
- Rotate webhook secrets regularly
- Use minimal token scopes
- Validate repository access
- Secure token storage

### 4. Performance
- Batch API requests when possible
- Implement response caching
- Use concurrent processing
- Monitor API usage

## Troubleshooting

### Common Issues

1. **API Rate Limits**
   - Monitor rate limit headers
   - Implement rate limit handling
   - Use conditional requests
   - Consider using GraphQL

2. **Webhook Delivery**
   - Check webhook configuration
   - Verify signature verification
   - Monitor delivery attempts
   - Check request payload

3. **Authentication**
   - Verify token permissions
   - Check token expiration
   - Validate repository access
   - Monitor auth errors

### Debugging Tools

1. Enable debug logging:
   ```python
   # Set log level to DEBUG
   LOG_LEVEL=DEBUG
   
   # Add detailed request logging
   logging.getLogger('aiohttp.client').setLevel(logging.DEBUG)
   ```

2. Monitor GitHub API usage:
   ```python
   # Check rate limit status
   curl -H "Authorization: token $GITHUB_TOKEN" \
        https://api.github.com/rate_limit
   ```

3. Webhook testing:
   ```bash
   # Test webhook endpoint
   curl -X POST http://localhost:8000/webhook \
        -H "X-GitHub-Event: pull_request" \
        -H "X-Hub-Signature-256: sha256=..." \
        -d @test_payload.json
   ```

## Support and Resources

1. **Documentation**
   - [GitHub REST API](https://docs.github.com/en/rest)
   - [Webhooks Guide](https://docs.github.com/en/webhooks)
   - [Authentication](https://docs.github.com/en/authentication)

2. **Tools**
   - GitHub API status: https://www.githubstatus.com/
   - API Explorer: https://docs.github.com/en/rest/overview/endpoints-available-for-github-apps
   - Webhook Tester: https://webhook.site/

3. **Community**
   - GitHub Community Forum
   - Stack Overflow with [github-api] tag
   - Project Issue Tracker