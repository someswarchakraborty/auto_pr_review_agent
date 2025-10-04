# MCP Integration Guide

## Overview

The PR Reviewer Agent uses the Model Context Protocol (MCP) to interact with GitHub repositories and perform intelligent code reviews. MCP provides a standardized way to access repository content, monitor changes, and post review comments.

## Configuration

### Environment Variables

```env
# MCP Configuration
MCP_ENDPOINT=https://mcp.github.dev/v1
MCP_TOKEN=your_mcp_token_here
MONITORED_REPOSITORIES=owner1/repo1,owner2/repo2
```

### Configuration File (settings.yaml)

```yaml
mcp:
  endpoint: ${MCP_ENDPOINT}
  token: ${MCP_TOKEN}
  repositories:
    - owner1/repo1
    - owner2/repo2
  review:
    batch_size: 10
    max_concurrent: 5
```

## MCP Features

### 1. PR Monitoring

The agent uses MCP to monitor repositories for new pull requests:

```python
# Example of PR monitoring through MCP
async def monitor_prs():
    client = MCPClient(endpoint, token)
    prs = await client.get_pending_reviews(repositories)
    for pr in prs:
        await process_pr(pr)
```

### 2. Code Analysis

MCP provides various code analysis capabilities:

- **Architecture Analysis**
  ```python
  # Validate architecture through MCP
  result = await mcp_client.validate_architecture(
      file_path="src/controller/UserController.java",
      rules=architecture_rules
  )
  ```

- **Context Analysis**
  ```python
  # Get file context
  context = await mcp_client.get_file_context(
      file_path="src/model/User.java",
      repository="owner/repo"
  )
  ```

### 3. Review Management

MCP handles the review lifecycle:

```python
# Post review through MCP
await mcp_client.post_review(
    repository="owner/repo",
    pr_number=123,
    review_result=result
)
```

## Working with MCP

### 1. Setting Up MCP

1. Obtain MCP credentials:
   ```bash
   # Request MCP access
   gh mcp auth login
   
   # Get MCP token
   gh mcp token create
   ```

2. Configure environment:
   ```bash
   # Set MCP environment variables
   export MCP_ENDPOINT="https://mcp.github.dev/v1"
   export MCP_TOKEN="your_token_here"
   ```

### 2. Repository Setup

1. Enable MCP for repositories:
   ```bash
   gh mcp repo enable owner/repo
   ```

2. Configure webhook (if needed):
   ```bash
   gh mcp webhook create owner/repo
   ```

### 3. Using MCP Client

The agent provides an `MCPClient` class for MCP interactions:

```python
from utils.mcp import MCPClient

# Initialize client
client = MCPClient(
    base_url=config.mcp_endpoint,
    auth_token=config.mcp_token
)

# Use MCP features
await client.analyze_pull_request(pr_context)
await client.get_file_context(file_path, repository)
await client.validate_architecture(file_path, content, rules)
```

## MCP Response Handling

### 1. Analysis Results

MCP returns analysis results in a standard format:

```json
{
  "issues": [
    {
      "severity": "error",
      "message": "Direct database access in controller",
      "file": "src/controller/UserController.java",
      "line": 45,
      "rule": "architecture.layer_violation"
    }
  ]
}
```

### 2. File Context

MCP provides rich context for files:

```json
{
  "language": "java",
  "imports": ["java.util.*", "org.springframework.*"],
  "classes": ["UserController"],
  "methods": ["getUser", "createUser"],
  "dependencies": ["Repository", "Service"]
}
```

## Error Handling

### 1. MCP Errors

Handle common MCP errors:

```python
try:
    result = await mcp_client.analyze_pull_request(pr)
except MCPConnectionError:
    # Handle connection issues
    logger.error("MCP connection failed")
except MCPAuthenticationError:
    # Handle auth issues
    logger.error("MCP authentication failed")
except MCPRateLimitError:
    # Handle rate limiting
    await asyncio.sleep(retry_after)
```

### 2. Recovery Strategies

1. **Connection Issues**:
   ```python
   # Implement exponential backoff
   retry_count = 0
   while retry_count < max_retries:
       try:
           return await mcp_client.analyze_pull_request(pr)
       except MCPConnectionError:
           await exponential_backoff(retry_count)
           retry_count += 1
   ```

2. **Rate Limiting**:
   ```python
   # Implement rate limit handling
   if isinstance(error, MCPRateLimitError):
       await asyncio.sleep(error.retry_after)
       return await mcp_client.analyze_pull_request(pr)
   ```

## Best Practices

1. **Error Handling**
   - Always implement proper error handling
   - Use exponential backoff for retries
   - Handle rate limits appropriately

2. **Performance**
   - Batch PR analysis when possible
   - Cache file context information
   - Use concurrent processing wisely

3. **Monitoring**
   - Log MCP interactions
   - Track error rates
   - Monitor response times

4. **Security**
   - Secure MCP tokens
   - Validate webhook payloads
   - Use HTTPS endpoints

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check MCP token validity
   - Verify token permissions
   - Ensure token is properly configured

2. **Rate Limiting**
   - Implement proper rate limiting handling
   - Use batch processing when possible
   - Monitor API usage

3. **Webhook Issues**
   - Verify webhook configuration
   - Check webhook secrets
   - Monitor webhook delivery

### Debugging

1. Enable debug logging:
   ```python
   # Enable MCP debug logging
   logging.getLogger('mcp').setLevel(logging.DEBUG)
   ```

2. Monitor MCP interactions:
   ```python
   # Track MCP requests
   await mcp_client.analyze_pull_request(pr, debug=True)
   ```

## Support

For MCP-related issues:
1. Check MCP status page
2. Review MCP documentation
3. Contact GitHub support
4. Check issue tracker