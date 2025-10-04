# Usage Guide

## Prerequisites

Before using the PR Reviewer Agent, ensure you have:

1. Python 3.11 or higher installed
2. Azure OpenAI API access configured
3. GitHub account with:
   - Personal access token with repo scope
   - Admin access to target repositories
4. ngrok installed (for local development)

## Getting Started

### 1. Environment Setup

Create a `.env` file with required configuration:

```env
# GitHub Configuration
GITHUB_TOKEN=your_github_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret
REPOSITORY_LIST=owner1/repo1,owner2/repo2

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT=your_deployment

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 2. Starting the Application

1. Start the FastAPI server:
```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Start the server
python src/main.py
```

2. In a separate terminal, start the webhook tunnel:
```powershell
# Start ngrok tunnel
python scripts/setup_tunnel.py
```

3. Configure GitHub webhook:
   - Copy the webhook URL from the tunnel setup output
   - Go to repository settings -> Webhooks
   - Add new webhook with:
     - Payload URL: `<tunnel-url>/webhook`
     - Content type: `application/json`
     - Secret: Your webhook secret
     - Events: Pull requests, Pull request reviews

### 3. Monitoring and Health Checks

1. Check application health:
```powershell
# Check health endpoint
Invoke-RestMethod http://localhost:8000/health

# Expected output:
{
    "status": "healthy",
    "github": true,
    "azure": true
}
```

2. Monitor logs:
```powershell
# Watch logs in real-time
Get-Content -Path .\logs\agent.log -Wait

# Filter for webhook events
Get-Content -Path .\logs\agent.log | Select-String "webhook"

# Check for errors
Get-Content -Path .\logs\agent.log | Select-String "ERROR"
```

## Using the PR Reviewer

### 1. Creating a Test PR

1. Create a new branch:
```powershell
git checkout -b feature/test-changes
```

2. Make some changes and commit:
```powershell
git add .
git commit -m "test: Add changes for testing PR review"
git push origin feature/test-changes
```

3. Create PR through GitHub UI:
   - Go to repository
   - Click "Compare & pull request"
   - Fill in PR details
   - Click "Create pull request"

### 2. Review Process

The agent automatically:

1. Detects new PR via webhook
2. Analyzes changed files for:
   - Security vulnerabilities
   - Code style issues
   - Best practices violations
   - API usage patterns
   - Documentation completeness

3. Provides feedback through:
   - Inline code comments
   - PR review summary
   - Status checks

### 3. Review Output

The agent generates:

1. **Security Analysis**
   ```
   🔴 Critical: Potential SQL injection vulnerability detected
   File: src/handlers/user.py:45
   Issue: Raw SQL query with string concatenation
   Fix: Use parameterized queries
   Example: cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
   ```

2. **Code Style Review**
   ```
   🟡 Warning: Method exceeds recommended length
   File: src/services/order.py:78
   Current: 52 lines
   Recommendation: Split into smaller functions for better maintainability
   ```

3. **Best Practices**
   ```
   💡 Suggestion: Consider adding error handling
   File: src/utils/api.py:23
   Context: API call without try-catch
   Recommendation: Implement proper error handling for API failures
   ```

## Understanding Review Output

### 1. Review Structure

Reviews are structured into categories:

1. **Critical Issues** (🔴)
   - Security vulnerabilities
   - Major architectural violations
   - Critical performance issues
   - Must be fixed before merging

2. **Warnings** (🟡)
   - Code style violations
   - Potential bugs
   - Performance concerns
   - Should be addressed but not blocking

3. **Suggestions** (💡)
   - Best practices
   - Code improvements
   - Documentation updates
   - Optional enhancements

4. **Information** (ℹ️)
   - Context and explanations
   - Resource links
   - Related documentation
   - Learning materials

### 2. Example Review

```
## PR Review Summary

Found 3 issues (1 critical, 1 warning, 1 suggestion)

### Critical Issues 🔴

1. SQL Injection Vulnerability
   File: src/handlers/user.py:45
   ```python
   query = f"SELECT * FROM users WHERE id = {user_id}"  # Unsafe
   ```
   Fix: Use parameterized queries
   ```python
   query = "SELECT * FROM users WHERE id = %s"
   cursor.execute(query, [user_id])
   ```

### Warnings 🟡

1. Large Function
   File: src/services/order.py:78
   - Function `process_order` is 52 lines long
   - Recommendation: Split into smaller functions
   - Suggested structure:
     - validate_order()
     - calculate_totals()
     - apply_discounts()
     - process_payment()

### Suggestions 💡

1. Error Handling
   File: src/utils/api.py:23
   - Add try-catch for API calls
   - Implement proper error logging
   - Consider retry mechanism
```

## Configuration

### 1. Analysis Settings

Edit `config/settings.yaml`:
```yaml
analysis:
  security:
    enabled: true
    severity_levels: ["critical", "high", "medium", "low"]
    
  code_style:
    enabled: true
    max_line_length: 100
    max_function_length: 50
    
  best_practices:
    enabled: true
    require_docstrings: true
    require_type_hints: true
```

### 2. Review Customization

Create `.github/pr_reviewer.yaml` in your repository:
```yaml
# Customize review behavior
review:
  ignore_patterns:
    - "tests/**/*_test.py"
    - "scripts/*.py"
  
  custom_rules:
    - name: "require_logging"
      pattern: "import logging"
      message: "Add logging to this file"
      severity: "warning"
      
  severity_overrides:
    max_line_length: "suggestion"
    missing_docstring: "warning"
```

## Troubleshooting

### Common Issues

1. **Webhook Not Receiving Events**
   ```powershell
   # Check ngrok status
   Get-Process -Name ngrok
   
   # Verify webhook endpoint
   Invoke-RestMethod http://localhost:8000/webhook
   
   # Check recent logs
   Get-Content -Path .\logs\agent.log -Tail 50
   ```

2. **GitHub API Issues**
   ```powershell
   # Check rate limits
   $headers = @{
       Authorization = "token $env:GITHUB_TOKEN"
   }
   Invoke-RestMethod https://api.github.com/rate_limit -Headers $headers
   
   # Verify token permissions
   Invoke-RestMethod https://api.github.com/user -Headers $headers
   ```

3. **Review Not Starting**
   ```powershell
   # Enable debug logging
   $env:LOG_LEVEL = "DEBUG"
   
   # Restart application
   Get-Process -Name python | 
       Where-Object { $_.CommandLine -like "*main.py*" } | 
       Stop-Process
   python src/main.py
   ```

### Getting Help

1. **Check Documentation**
   - [Setup Guide](setup.md)
   - [Configuration Guide](configuration.md)
   - [Troubleshooting Guide](troubleshooting.md)

2. **System Status**
   ```powershell
   # Check all components
   $components = @(
       "http://localhost:8000/health",
       (Get-Process python).Count,
       (Get-Process ngrok).Count,
       (Test-Path .env),
       (Test-Path config/settings.yaml)
   )
   
   $components | ForEach-Object {
       Write-Host "Status: $_"
   }
   ```

3. **Get Support**
   - Open an issue on GitHub
   - Check existing issues
   - Review error logs
   - Contact maintainers