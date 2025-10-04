# Troubleshooting Guide

## Common Issues and Solutions

### Application Issues

1. **FastAPI Server Not Starting**

   Symptoms:
   - Application fails to start
   - Port binding errors
   - Import errors
   - No logs being generated

   Solutions:
   ```bash
   # Check if port 8000 is already in use
   netstat -ano | findstr :8000

   # Verify Python environment
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt

   # Check configuration
   python -m src.core.config

   # Verify logs directory exists and is writable
   mkdir -p logs
   ```

2. **Webhook Tunnel Issues**

   Symptoms:
   - ngrok tunnel not starting
   - 404 errors on webhook endpoint
   - Webhook URL not accessible

   Solutions:
   ```bash
   # Check if ngrok is running
   tasklist | findstr ngrok

   # Kill existing ngrok processes
   taskkill /F /IM ngrok.exe

   # Restart tunnel with debug logging
   $env:DEBUG="*"; python scripts/setup_tunnel.py
   ```

2. **Review Timeout**

   Symptoms:
   - Reviews incomplete
   - Timeout errors in logs

   Solutions:
   ```yaml
   # Increase timeout in settings.yaml
   agent:
     review_timeout: 600  # Increase from default 300

   # Or split large PRs
   agent:
     max_files_per_review: 50
   ```

### Integration Issues

1. **GitHub API Issues**

   Symptoms:
   - Cannot fetch PR data
   - Authentication errors
   - Rate limit exceeded
   - Webhook delivery failures

   Solutions:
   ```powershell
   # Test GitHub API connectivity
   $headers = @{
       Authorization = "token $env:GITHUB_TOKEN"
   }
   Invoke-RestMethod -Uri "https://api.github.com/user" -Headers $headers

   # Check rate limits
   Invoke-RestMethod -Uri "https://api.github.com/rate_limit" -Headers $headers

   # Verify webhook deliveries
   # Go to repository settings -> Webhooks -> Recent Deliveries
   ```

2. **Webhook Issues**

   Symptoms:
   - Webhook not receiving events
   - Signature verification failures
   - 401/403 errors in GitHub webhook logs

   Solutions:
   ```powershell
   # Verify webhook secret
   if ($env:GITHUB_WEBHOOK_SECRET) {
       Write-Host "Webhook secret is set"
   } else {
       Write-Host "Webhook secret is missing"
   }

   # Test webhook endpoint locally
   Invoke-RestMethod -Uri "http://localhost:8000/webhook" -Method GET

   # Check FastAPI logs
   Get-Content -Path .\logs\agent.log -Tail 50
   ```

3. **Azure OpenAI Issues**

   Symptoms:
   - LLM responses failing
   - Token/quota errors
   - Timeout errors
   - Invalid deployment errors

   Solutions:
   ```powershell
   # Verify Azure OpenAI credentials
   $headers = @{
       "api-key" = $env:AZURE_OPENAI_API_KEY
   }
   $endpoint = "$env:AZURE_OPENAI_ENDPOINT/openai/deployments?api-version=2023-05-15"
   Invoke-RestMethod -Uri $endpoint -Headers $headers -Method GET

   # Check deployment status
   $deployment = "$env:AZURE_OPENAI_ENDPOINT/openai/deployments/$env:AZURE_OPENAI_DEPLOYMENT"
   Invoke-RestMethod -Uri "$deployment?api-version=2023-05-15" -Headers $headers -Method GET
   ```

### Analyzer Issues

1. **False Positives**

   Symptoms:
   - Too many irrelevant issues
   - Incorrect rule matches

   Solutions:
   ```yaml
   # Adjust rule sensitivity
   rules:
     architecture:
       sensitivity: 0.8  # Default 0.7

   # Add exclusions
   excludes:
     - "test/*"
     - "legacy/*"
   ```

2. **Missing Issues**

   Symptoms:
   - Known issues not detected
   - Rules not triggering

   Solutions:
   ```yaml
   # Enable debug logging
   logging:
     level: DEBUG
     analyzers: true

   # Verify rule patterns
   python -m src.tools.verify_rules
   ```

## Diagnostic Tools

### Log Analysis

1. **Viewing Application Logs**
   ```powershell
   # Show recent logs with live updates
   Get-Content -Path .\logs\agent.log -Wait

   # Filter error logs
   Get-Content -Path .\logs\agent.log | Select-String -Pattern "ERROR"

   # Show webhook events
   Get-Content -Path .\logs\agent.log | Select-String -Pattern "webhook"
   ```

2. **Log Configuration**
   ```python
   # In .env file
   LOG_LEVEL=DEBUG  # Options: DEBUG, INFO, WARNING, ERROR
   
   # In settings.yaml
   logging:
     level: ${LOG_LEVEL}
     format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
     file: logs/agent.log
   ```

3. **Log Analysis Scripts**
   ```powershell
   # Analyze webhook success rate
   Get-Content -Path .\logs\agent.log | 
       Select-String -Pattern "(webhook.*success|webhook.*error)" | 
       Group-Object { $_.Line -match "error" } | 
       Select-Object Count,Name

   # Check API rate limits
   Get-Content -Path .\logs\agent.log | 
       Select-String -Pattern "rate limit" -Context 2,0
   ```

### Performance Analysis

1. **Resource Monitoring**
   ```powershell
   # Monitor FastAPI process
   Get-Process -Name python | 
       Where-Object { $_.CommandLine -like "*main.py*" } | 
       Select-Object CPU,WorkingSet,Handles

   # Check ngrok process
   Get-Process -Name ngrok | 
       Select-Object CPU,WorkingSet,Handles
   ```

2. **API Performance**
   ```powershell
   # Monitor API response times
   Get-Content -Path .\logs\agent.log | 
       Select-String -Pattern "Request completed in \d+\.\d+s" | 
       ForEach-Object { $_.Matches.Value }

   # Check webhook processing times
   Get-Content -Path .\logs\agent.log | 
       Select-String -Pattern "Processing GitHub webhook.*completed in" | 
       ForEach-Object { $_.Line }
   ```

### System Validation

1. **Environment Validation**
   ```powershell
   # Check required environment variables
   $required = @(
       "GITHUB_TOKEN",
       "GITHUB_WEBHOOK_SECRET",
       "AZURE_OPENAI_API_KEY",
       "AZURE_OPENAI_ENDPOINT"
   )
   foreach ($var in $required) {
       if ([Environment]::GetEnvironmentVariable($var)) {
           Write-Host "$var is set"
       } else {
           Write-Host "$var is missing" -ForegroundColor Red
       }
   }
   ```

2. **Connectivity Tests**
   ```powershell
   # Test all endpoints
   $endpoints = @(
       "http://localhost:8000/health",
       "https://api.github.com",
       $env:AZURE_OPENAI_ENDPOINT
   )
   foreach ($endpoint in $endpoints) {
       try {
           $response = Invoke-RestMethod -Uri $endpoint
           Write-Host "$endpoint is accessible"
       } catch {
           Write-Host "$endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
       }
   }
   ```

## Recovery Procedures

### Application Recovery

1. **FastAPI Server Reset**
   ```powershell
   # Stop the server
   Get-Process -Name python | 
       Where-Object { $_.CommandLine -like "*main.py*" } | 
       Stop-Process

   # Restart with fresh logs
   Move-Item .\logs\agent.log .\logs\agent.log.old
   Start-Process python -ArgumentList "src/main.py"
   ```

2. **Tunnel Recovery**
   ```powershell
   # Reset ngrok tunnel
   Get-Process -Name ngrok | Stop-Process
   python scripts/setup_tunnel.py
   ```

### Integration Recovery

1. **Webhook Recovery**
   ```powershell
   # Reset webhook configuration
   # 1. Delete webhook in GitHub settings
   # 2. Stop ngrok tunnel
   Get-Process -Name ngrok | Stop-Process
   
   # 3. Start fresh tunnel
   python scripts/setup_tunnel.py
   
   # 4. Configure new webhook with fresh URL
   ```

2. **GitHub Integration Reset**
   ```powershell
   # Clear GitHub token
   $env:GITHUB_TOKEN = ""
   
   # Generate new token in GitHub
   # Update .env file with new token
   
   # Restart application
   Get-Process -Name python | 
       Where-Object { $_.CommandLine -like "*main.py*" } | 
       Stop-Process
   python src/main.py
   ```

## Prevention Measures

### 1. Monitoring and Alerts

1. **Application Monitoring**
   ```powershell
   # Create monitoring script (monitor.ps1)
   while ($true) {
       # Check FastAPI health
       try {
           $health = Invoke-RestMethod "http://localhost:8000/health"
           Write-Host "API Status: $($health.status)"
       } catch {
           Write-Host "API Error: $_" -ForegroundColor Red
           # Send alert (implement your alert mechanism)
       }
       
       # Check ngrok tunnel
       $ngrok = Get-Process -Name ngrok -ErrorAction SilentlyContinue
       if (-not $ngrok) {
           Write-Host "Tunnel Down!" -ForegroundColor Red
           # Send alert
       }
       
       Start-Sleep -Seconds 300  # Check every 5 minutes
   }
   ```

2. **GitHub Integration Monitoring**
   ```powershell
   # Monitor webhook deliveries (webhook_monitor.ps1)
   Get-Content -Path .\logs\agent.log -Wait | ForEach-Object {
       if ($_ -match "webhook.*error") {
           Write-Host "Webhook Error: $_" -ForegroundColor Red
           # Send alert
       }
       if ($_ -match "rate limit exceeded") {
           Write-Host "Rate Limit Warning: $_" -ForegroundColor Yellow
           # Send alert
       }
   }
   ```

### 2. Backup and Recovery

1. **Configuration Backup**
   ```powershell
   # Create backup script (backup_config.ps1)
   $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
   $backup_dir = "backups/$timestamp"

   # Create backup directory
   New-Item -ItemType Directory -Path $backup_dir -Force

   # Backup configuration files
   Copy-Item .env "$backup_dir/.env"
   Copy-Item config/* $backup_dir/config/ -Recurse
   Copy-Item logs/* $backup_dir/logs/ -Recurse

   # Maintain backup history (keep last 7 days)
   Get-ChildItem backups | Where-Object {
       $_.LastWriteTime -lt (Get-Date).AddDays(-7)
   } | Remove-Item -Recurse -Force
   ```

2. **Environment Snapshots**
   ```powershell
   # Create environment snapshot (snapshot.ps1)
   $snapshot = @{
       Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
       Python = (python --version)
       Dependencies = (pip freeze)
       Environment = @{}
   }

   # Capture environment variables
   Get-ChildItem env: | Where-Object {
       $_.Name -match "(GITHUB|AZURE|LOG)"
   } | ForEach-Object {
       $snapshot.Environment[$_.Name] = $_.Value
   }

   # Save snapshot
   $snapshot | ConvertTo-Json | 
       Set-Content "snapshots/env_$(Get-Date -Format 'yyyyMMdd').json"
   ```

### 3. Automated Health Checks

1. **System Health Check Script**
   ```powershell
   # Create health check script (health_check.ps1)
   function Test-SystemHealth {
       $checks = @(
           @{
               Name = "FastAPI Server"
               Test = { Invoke-RestMethod "http://localhost:8000/health" }
           }
           @{
               Name = "Ngrok Tunnel"
               Test = { Get-Process -Name ngrok }
           }
           @{
               Name = "GitHub API"
               Test = { 
                   Invoke-RestMethod `
                       -Uri "https://api.github.com/rate_limit" `
                       -Headers @{
                           Authorization = "token $env:GITHUB_TOKEN"
                       }
               }
           }
       )

       foreach ($check in $checks) {
           try {
               $result = & $check.Test
               Write-Host "$($check.Name): OK" -ForegroundColor Green
           } catch {
               Write-Host "$($check.Name): Failed - $_" -ForegroundColor Red
               # Implement recovery actions
           }
       }
   }

   # Run health check every 5 minutes
   while ($true) {
       Test-SystemHealth
       Start-Sleep -Seconds 300
   }
   ```

2. **Auto-Recovery Actions**
   ```powershell
   # Create recovery script (auto_recover.ps1)
   function Restart-FastAPI {
       Get-Process -Name python | 
           Where-Object { $_.CommandLine -like "*main.py*" } | 
           Stop-Process
       Start-Process python -ArgumentList "src/main.py"
   }

   function Restart-Tunnel {
       Get-Process -Name ngrok | Stop-Process
       Start-Process python -ArgumentList "scripts/setup_tunnel.py"
   }

   # Watch for issues and auto-recover
   Get-Content -Path .\logs\agent.log -Wait | ForEach-Object {
       if ($_ -match "Application crash") {
           Write-Host "Restarting FastAPI..." -ForegroundColor Yellow
           Restart-FastAPI
       }
       if ($_ -match "Tunnel disconnected") {
           Write-Host "Restarting tunnel..." -ForegroundColor Yellow
           Restart-Tunnel
       }
   }
   ```