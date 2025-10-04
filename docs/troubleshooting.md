# Troubleshooting Guide

## Common Issues and Solutions

### Agent Issues

1. **Agent Not Starting**

   Symptoms:
   - Service fails to start
   - No logs being generated

   Solutions:
   ```bash
   # Check configuration
   python -m src.tools.config_validator

   # Verify environment variables
   python -m src.tools.env_checker

   # Check permissions
   python -m src.tools.permission_checker
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

1. **GitHub Connection**

   Symptoms:
   - Cannot fetch PR data
   - Webhook errors

   Solutions:
   ```bash
   # Test GitHub connection
   python -m src.tools.test_github_connection

   # Verify webhook
   python -m src.tools.verify_webhook
   ```

2. **Azure OpenAI Issues**

   Symptoms:
   - LLM responses failing
   - Token errors

   Solutions:
   ```bash
   # Test Azure OpenAI connection
   python -m src.tools.test_azure_connection

   # Check rate limits
   python -m src.tools.check_rate_limits
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

1. **Viewing Logs**
   ```bash
   # Show recent logs
   tail -f logs/agent.log

   # Filter error logs
   grep ERROR logs/agent.log

   # Show review timing
   python -m src.tools.analyze_timing
   ```

2. **Log Levels**
   ```yaml
   logging:
     file: logs/agent.log
     level: DEBUG  # or INFO, WARNING, ERROR
     format: detailed  # or simple
   ```

### Performance Analysis

1. **Resource Usage**
   ```bash
   # Monitor CPU/Memory
   python -m src.tools.monitor_resources

   # Check review timing
   python -m src.tools.review_stats
   ```

2. **Profile Code**
   ```bash
   # Run with profiling
   python -m cProfile -o profile.stats src/main.py

   # Analyze profile
   python -m src.tools.analyze_profile
   ```

### Configuration Validation

1. **Validate Settings**
   ```bash
   # Check configuration
   python -m src.tools.validate_config

   # Test rule patterns
   python -m src.tools.test_rules
   ```

2. **Environment Check**
   ```bash
   # Verify environment
   python -m src.tools.check_env

   # Test integrations
   python -m src.tools.test_integrations
   ```

## Recovery Procedures

### Service Recovery

1. **Restart Procedure**
   ```bash
   # Safe restart
   python -m src.tools.safe_restart

   # Emergency restart
   python -m src.tools.force_restart
   ```

2. **Data Recovery**
   ```bash
   # Backup configuration
   python -m src.tools.backup_config

   # Restore configuration
   python -m src.tools.restore_config
   ```

### Error Recovery

1. **Failed Reviews**
   ```bash
   # Retry failed reviews
   python -m src.tools.retry_reviews

   # Clear stuck reviews
   python -m src.tools.clear_stuck
   ```

2. **Integration Recovery**
   ```bash
   # Reset webhooks
   python -m src.tools.reset_webhooks

   # Reconnect integrations
   python -m src.tools.reconnect
   ```

## Prevention Measures

1. **Monitoring Setup**
   ```yaml
   monitoring:
     enabled: true
     metrics:
       - review_time
       - error_rate
       - success_rate
     alerts:
       - type: error_spike
         threshold: 5
       - type: timeout
         threshold: 300
   ```

2. **Backup Configuration**
   ```yaml
   backup:
     enabled: true
     interval: 24h
     retain: 7
     include:
       - config/*
       - rules/*
   ```

3. **Health Checks**
   ```yaml
   health_check:
     enabled: true
     interval: 5m
     endpoints:
       - /health
       - /metrics
     actions:
       - restart_on_fail: true
       - notify: true
   ```