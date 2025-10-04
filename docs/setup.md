# Setup Instructions

This guide provides comprehensive setup instructions for the PR Reviewer Agent, including local development and production deployment configurations.

## Prerequisites

### Required Software
1. Python 3.11 or higher
2. Git
3. ngrok (for local development)
4. Docker (optional, for containerized deployment)

### Required Accounts and Access
1. GitHub account with:
   - Repository admin access
   - Personal Access Token with repo scope
2. Azure OpenAI API access:
   - API key
   - Endpoint URL
   - Deployment name

## Installation

### 1. Repository Setup
```bash
# Clone the repository
git clone https://github.com/someswarchakraborty/auto_pr_review_agent.git
cd auto_pr_review_agent

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # On Windows
source venv/bin/activate # On Unix/MacOS

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory with the following configuration:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT=your_deployment_name

# GitHub Configuration
GITHUB_TOKEN=your_github_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret
REPOSITORY_LIST=owner1/repo1,owner2/repo2

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 3. Application Configuration

Configure the agent settings in `config/settings.yaml`:

```yaml
agent:
  review_timeout: 300  # seconds
  max_files: 100
  concurrent_reviews: 5
  retry_attempts: 3
  retry_delay: 5

analysis:
  style_check: true
  security_check: true
  architecture_check: true
  test_coverage: true
  documentation: true

github:
  webhook_events:
    - pull_request
    - pull_request_review
  api_version: "2022-11-28"
  max_comments_per_review: 50

logging:
  level: ${LOG_LEVEL}
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: logs/agent.log
```

## Local Development Setup

### 1. Start the FastAPI Application
```bash
# Start with auto-reload for development
python src/main.py
```

### 2. Setup Webhook Tunnel
In a separate terminal:
```bash
# Start the ngrok tunnel
python scripts/setup_tunnel.py
```

### 3. Configure GitHub Webhook
Follow the instructions printed by the tunnel script to:
1. Copy the webhook URL
2. Configure the webhook in GitHub repository settings
3. Set the webhook secret
4. Select webhook events

## Testing the Setup

### 1. Verify API Health
```bash
curl http://localhost:8000/health
```

### 2. Create a Test PR
```bash
# Create a test branch
git checkout -b feature/test-security-issues

# Make changes and commit
git add .
git commit -m "test: Add security test cases"
git push origin feature/test-security-issues

# Create PR through GitHub UI
```

### 3. Monitor Logs
```bash
# Watch the application logs
Get-Content -Path .\logs\agent.log -Wait  # PowerShell
tail -f logs/agent.log                    # Unix/MacOS
```

## Production Deployment

### Docker Deployment

1. Build the container:
```bash
docker build -t pr-reviewer-agent .
```

2. Run the container:
```bash
docker run -d --name pr-reviewer \
  -p 8000:8000 \
  -v ${PWD}/logs:/app/logs \
  -v ${PWD}/config:/app/config \
  --env-file .env \
  pr-reviewer-agent
```

### Production Configuration

1. Update environment variables:
```env
ENVIRONMENT=production
LOG_LEVEL=WARNING
```

2. Configure a reverse proxy (nginx recommended):
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring and Maintenance

### 1. Log Monitoring
- Set up log rotation:
```bash
logrotate -s /var/log/logstatus /etc/logrotate.d/pr-reviewer
```

### 2. Health Checks
- Monitor the /health endpoint
- Set up uptime monitoring
- Configure alerts for errors

### 3. Backup
- Regularly backup configuration files
- Maintain backup of logs
- Document environment settings

## Troubleshooting

### Common Issues

1. Webhook 404 Errors
   - Verify ngrok tunnel is running
   - Check webhook URL configuration
   - Ensure FastAPI server is running

2. Authentication Failures
   - Verify GitHub token permissions
   - Check webhook secret configuration
   - Validate Azure OpenAI credentials

3. Rate Limiting
   - Check GitHub API rate limits
   - Monitor Azure OpenAI usage
   - Adjust concurrent review settings

### Getting Help

1. Check the logs:
```bash
Get-Content -Path .\logs\agent.log -Tail 100
```

2. Enable debug logging:
```bash
# Update .env
LOG_LEVEL=DEBUG
```

3. Review documentation:
   - [Troubleshooting Guide](troubleshooting.md)
   - [GitHub API Documentation](https://docs.github.com/en/rest)
   - [FastAPI Documentation](https://fastapi.tiangolo.com/)