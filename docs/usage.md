# Usage Guide

## Prerequisites

Before using the PR Reviewer Agent, ensure you have:

1. Azure OpenAI API access configured
2. GitHub access token with repository permissions
3. MCP access token and endpoint configured
4. Required repositories enabled for MCP

For MCP-specific setup, see [MCP Integration Guide](mcp_integration.md).

## Basic Usage

### 1. Starting the Agent

```bash
# From the project root directory
python src/main.py
```

The agent will start monitoring configured repositories for new pull requests.

Note: The application will automatically set up the Python path. Just make sure you're running the command from the project root directory.

### 2. Monitoring Agent Status

Access the agent's status dashboard at `http://localhost:8000/status`

### 3. Viewing Review Results

Reviews can be found:
- As comments on the GitHub PR
- In the agent's dashboard
- In the logs directory

## Review Process

### What Gets Reviewed

The agent analyzes:
1. Code style and formatting
2. Potential security vulnerabilities
3. Architectural compliance
4. API usage patterns
5. Code quality metrics

### Review Output

The agent provides:
1. Inline comments on specific code issues
2. A summary comment with overall findings
3. Suggestions for improvements
4. Security vulnerability alerts
5. Architecture violation warnings

## Understanding Review Comments

### Comment Types

1. **Error** (🔴): Must be fixed before merging
2. **Warning** (🟡): Should be addressed but not blocking
3. **Suggestion** (💡): Optional improvements
4. **Info** (ℹ️): Additional context or information

### Example Comments

```
🔴 Error: Direct database access in controller detected
Location: src/controller/UserController.java:45
Suggestion: Move database operations to the repository layer
```

```
💡 Suggestion: Consider extracting this logic into a separate method
Current method length: 52 lines
Recommended max length: 30 lines
```

## Customization

### Ignoring Rules

Add a `.prreviewerrc` file to your repository:
```yaml
ignore:
  - rule: "max_method_length"
    files: ["*/test/*"]
  - rule: "no_db_in_controller"
    files: ["*/legacy/*"]
```

### Custom Rules

See [configuration.md](configuration.md) for adding custom rules.

## Troubleshooting

### Common Issues

1. **Review Timeout**
   - Increase `review_timeout` in settings
   - Reduce PR size
   - Check network connectivity

2. **False Positives**
   - Add rule exceptions in `.prreviewerrc`
   - Adjust rule severity in settings
   - Submit feedback through the dashboard

3. **Missing Reviews**
   - Verify webhook configuration
   - Check GitHub permissions
   - Review agent logs

### Getting Help

1. Check the logs in `logs/agent.log`
2. Review the documentation
3. Submit an issue on GitHub
4. Contact support team