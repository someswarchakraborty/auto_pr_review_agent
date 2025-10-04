# Configuration Guide

## Agent Configuration

The agent's behavior can be customized through various configuration files and environment variables.

### Environment Variables

```env
AZURE_OPENAI_API_KEY=     # Your Azure OpenAI API key
AZURE_OPENAI_ENDPOINT=    # Azure OpenAI endpoint URL
GITHUB_TOKEN=            # GitHub personal access token
LOG_LEVEL=              # Logging level (DEBUG, INFO, WARNING, ERROR)
```

### Agent Settings (settings.yaml)

```yaml
agent:
  # Review timeout in seconds
  review_timeout: 300
  
  # Maximum number of files to review in a PR
  max_files: 100
  
  # Number of concurrent reviews
  concurrent_reviews: 5

analysis:
  # Enable/disable specific checks
  style_check: true
  security_check: true
  architecture_check: true
  
  # Severity levels for different types of issues
  severity_levels:
    style: "low"
    security: "high"
    architecture: "medium"

rules:
  # Architecture rules
  architecture:
    - name: "no_db_in_controller"
      pattern: "repository\\.|EntityManager\\."
      scope: "*/controller/*"
      message: "Direct database access in controller layer is not allowed"

  # Coding standards
  coding_standards:
    - name: "max_method_length"
      value: 50
      message: "Method is too long. Consider breaking it down"

  # Security rules
  security:
    - name: "sql_injection"
      pattern: "execute\\(|executeQuery\\("
      message: "Potential SQL injection vulnerability"

# LLM Configuration
llm:
  model: "gpt-4"
  temperature: 0.1
  max_tokens: 2000
```

## Rule Customization

### Adding Custom Rules

1. Create a new rule in `settings.yaml`:
```yaml
rules:
  architecture:
    - name: "custom_rule"
      pattern: "your_pattern"
      scope: "file_pattern"
      message: "Your message"
```

2. Implement the rule handler in `src/analyzers/rules/custom_rules.py`

### Rule Priority

Rules are evaluated in the following order:
1. Security rules
2. Architecture rules
3. Coding standards
4. Custom rules

## Integration Settings

### GitHub Integration

Configure GitHub webhook settings in `config/github_config.yaml`:
```yaml
webhook:
  events:
    - pull_request
    - pull_request_review
  branches:
    - main
    - develop
```