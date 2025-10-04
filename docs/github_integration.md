# GitHub Integration Guide

## Overview

The PR Review Agent uses GitHub's REST API and webhook system to interact with repositories and perform intelligent code reviews. This integration enables real-time monitoring of pull requests, automated code analysis, and direct feedback through PR comments.

## Integration Methods

### 1. GitHub REST API

The application uses GitHub's REST API v3 for:
- Pull request management and monitoring
- File content retrieval
- Comment and review submission
- Repository metadata access

### 2. Webhook Integration

Webhook system provides:
- Real-time event notifications
- Secure payload delivery with signature verification
- Configurable event filtering
- Automatic retry mechanism

## Configuration

### 1. Environment Variables

```env
# GitHub Configuration
GITHUB_TOKEN=your_personal_access_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret
REPOSITORY_LIST=owner1/repo1,owner2/repo2

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 2. Application Settings

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
```

## Setup Instructions

### 1. GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with scopes:
   - `repo` (Full control of private repositories)
   - `read:org` (Read organization data)
   - `workflow` (Optional, if using GitHub Actions)

### 2. Webhook Configuration

1. Start the tunnel for local development:
   ```powershell
   python scripts/setup_tunnel.py
   ```

2. In GitHub repository settings:
   - Go to Settings → Webhooks → Add webhook
   - Payload URL: Use the URL from tunnel setup
   - Content type: `application/json`
   - Secret: Generate a secure random string
   - Events: Select 'Pull requests' and 'Pull request reviews'
   - Enable SSL verification

### 3. Repository Setup

1. Configure repository access:
   ```env
   REPOSITORY_LIST=owner1/repo1,owner2/repo2
   ```

2. Verify repository permissions:
   ```powershell
   # Test repository access
   $headers = @{
       Authorization = "token $env:GITHUB_TOKEN"
   }
   Invoke-RestMethod -Uri "https://api.github.com/repos/owner/repo" -Headers $headers
   ```

## GitHub API Integration

### 1. API Client Implementation

```python
class GitHubClient:
    """GitHub API client with retry and rate limit handling."""
    
    def __init__(self, token: str, base_url: str = "https://api.github.com"):
        """Initialize GitHub client with authentication."""
        self.session = aiohttp.ClientSession(headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "PR-Review-Agent"
        })
        self.base_url = base_url
        self.rate_limiter = RateLimiter()

    async def get_pull_request(self, repo: str, pr_number: int) -> dict:
        """Get PR details with automatic retry and rate limit handling."""
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}"
        return await self._make_request("GET", url)

    async def create_review(self, repo: str, pr_number: int, 
                          review: dict) -> dict:
        """Create a review on a pull request."""
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}/reviews"
        return await self._make_request("POST", url, json=review)
```

### 2. Webhook Handler Implementation

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

## Error Handling

### 1. Rate Limit Handling

```python
class RateLimiter:
    """Handle GitHub API rate limits."""
    
    async def check_rate_limit(self):
        """Check current rate limit status."""
        response = await self._make_request("GET", "/rate_limit")
        return response["resources"]["core"]

    async def handle_rate_limit(self, response: ClientResponse):
        """Handle rate limit exceeded response."""
        reset_time = int(response.headers["X-RateLimit-Reset"])
        sleep_time = reset_time - time.time()
        if sleep_time > 0:
            logger.warning(f"Rate limit exceeded. Sleeping for {sleep_time}s")
            await asyncio.sleep(sleep_time)
```

### 2. Retry Strategy

```python
class RetryHandler:
    """Handle retries with exponential backoff."""
    
    async def with_retry(self, func, *args, max_attempts: int = 3, 
                        initial_delay: float = 1.0):
        """Execute function with retry logic."""
        for attempt in range(max_attempts):
            try:
                return await func(*args)
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise
                delay = initial_delay * (2 ** attempt)
                logger.warning(f"Retry {attempt + 1}/{max_attempts} "
                             f"after {delay}s: {str(e)}")
                await asyncio.sleep(delay)
```

## Security Best Practices

### 1. Authentication Security

- Store tokens securely using environment variables
- Use minimal required token scopes
- Rotate tokens periodically
- Monitor token usage

### 2. Webhook Security

- Validate all webhook signatures
- Use strong webhook secrets
- Enable SSL verification
- Monitor webhook deliveries

### 3. Data Protection

- Sanitize logged data
- Protect sensitive information
- Validate repository access
- Monitor API usage

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify token validity and permissions
   - Check token scopes
   - Ensure proper token format

2. **Webhook Errors**
   - Verify webhook URL accessibility
   - Check signature calculation
   - Validate event payload
   - Monitor webhook deliveries

3. **Rate Limiting**
   - Monitor rate limit headers
   - Implement proper backoff
   - Consider using conditional requests
   - Cache responses when possible

### Debugging Tools

1. **API Testing**
   ```powershell
   # Test API access
   $headers = @{
       Authorization = "token $env:GITHUB_TOKEN"
   }
   Invoke-RestMethod -Uri "https://api.github.com/user" -Headers $headers
   ```

2. **Webhook Testing**
   ```powershell
   # Test webhook endpoint
   $body = @{
       action = "test"
       repository = @{
           full_name = "owner/repo"
       }
   } | ConvertTo-Json
   
   Invoke-RestMethod -Uri "http://localhost:8000/webhook" `
                    -Method Post `
                    -Body $body `
                    -Headers @{
                        "X-GitHub-Event" = "ping"
                        "Content-Type" = "application/json"
                    }
   ```

## Monitoring and Maintenance

### 1. Health Checks

- Regular API connectivity tests
- Webhook delivery monitoring
- Rate limit tracking
- Token validity verification

### 2. Performance Monitoring

- Track API response times
- Monitor rate limit usage
- Watch webhook processing times
- Log error rates

### 3. Regular Maintenance

- Update API version when needed
- Rotate webhook secrets
- Review token permissions
- Update documentation

## Resources

1. **GitHub Documentation**
   - [REST API v3](https://docs.github.com/en/rest)
   - [Webhooks Guide](https://docs.github.com/en/webhooks)
   - [Authentication](https://docs.github.com/en/authentication)

2. **Tools and Utilities**
   - [GitHub API Status](https://www.githubstatus.com/)
   - [API Explorer](https://api.github.com)
   - [Webhook Tester](https://webhook.site)

3. **Support Resources**
   - GitHub Support Portal
   - Stack Overflow [github-api]
   - GitHub Community Forum