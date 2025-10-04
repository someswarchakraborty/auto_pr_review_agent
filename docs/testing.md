# Testing Strategy

## Overview

This document outlines the testing strategy for the PR Review Agent, including test cases, expected outcomes, and validation procedures. The strategy covers unit testing, integration testing, and end-to-end testing scenarios.

## Test Categories

### 1. Unit Tests

Location: `tests/unit/`

#### Core Components Testing

1. **Analyzer Tests**
   ```python
   # tests/unit/analyzers/test_security_analyzer.py
   def test_sql_injection_detection():
       analyzer = SecurityAnalyzer()
       code = """
       def get_user(user_id):
           cursor.execute("SELECT * FROM users WHERE id = " + user_id)
       """
       results = await analyzer.analyze(code, "app/db/queries.py")
       assert len(results) == 1
       assert results[0].severity == "critical"
       assert "SQL injection" in results[0].message
   ```

2. **GitHub Client Tests**
   ```python
   # tests/unit/utils/test_github_client.py
   def test_rate_limit_handling():
       client = GitHubClient(token="test")
       with mock_response(status=429, headers={"X-RateLimit-Reset": "123"}):
           with pytest.raises(RateLimitExceeded):
               await client.get_pull_request("owner/repo", 1)
   ```

### 2. Integration Tests

Location: `tests/integration/`

#### Webhook Processing Tests
```python
# tests/integration/test_webhook_handler.py
async def test_webhook_signature_verification():
    body = b'{"action": "opened"}'
    secret = "test_secret"
    signature = generate_signature(body, secret)
    response = await client.post(
        "/webhook",
        headers={"X-Hub-Signature-256": signature},
        content=body
    )
    assert response.status_code == 200
```

### 3. End-to-End Tests

Location: `tests/e2e/`

#### PR Review Flow Test
```python
# tests/e2e/test_pr_review.py
async def test_complete_review_flow():
    # Create test PR with security issues
    pr = await create_test_pr("test_security.py")
    
    # Wait for webhook event processing
    await wait_for_review(pr.number)
    
    # Verify review comments
    comments = await get_pr_comments(pr.number)
    assert any("SQL injection vulnerability" in c.body for c in comments)
```

## Security Test Cases

The following section details our security test cases and expected analyzer responses.

### Test File: `security_test.py`

```python
# Contains intentional security issues for testing
def insecure_db_query(user_input):
    query = f"SELECT * FROM users WHERE id = {user_input}"  # SQL Injection
    cursor.execute(query)

def weak_crypto():
    cipher = DES.new(key, DES.MODE_ECB)  # Weak Encryption
    return cipher.encrypt(data)

def hardcoded_secrets():
    api_key = "1234567890abcdef"  # Hardcoded Secret
    password = "admin123"  # Hardcoded Password

def command_injection(user_input):
    os.system(f"ping {user_input}")  # Command Injection

def insecure_deserialize(data):
    return pickle.loads(data)  # Insecure Deserialization
```

### Expected Analysis Output

```json
{
  "summary": {
    "total_issues": 5,
    "critical": 2,
    "high": 2,
    "medium": 1,
    "file": "security_test.py"
  },
  "issues": [
    {
      "severity": "critical",
      "type": "sql_injection",
      "line": 3,
      "message": "SQL Injection vulnerability detected: User input is directly concatenated into SQL query",
      "snippet": "query = f\"SELECT * FROM users WHERE id = {user_input}\"",
      "recommendation": "Use parameterized queries: cursor.execute(\"SELECT * FROM users WHERE id = %s\", [user_input])",
      "cwe": "CWE-89"
    },
    {
      "severity": "high",
      "type": "weak_crypto",
      "line": 7,
      "message": "Use of weak cryptographic algorithm (DES) in ECB mode",
      "snippet": "cipher = DES.new(key, DES.MODE_ECB)",
      "recommendation": "Use AES-GCM or ChaCha20-Poly1305 for encryption",
      "cwe": "CWE-326"
    },
    {
      "severity": "high",
      "type": "hardcoded_secret",
      "line": 10,
      "message": "Hardcoded API key and password detected",
      "snippet": "api_key = \"1234567890abcdef\"",
      "recommendation": "Use environment variables or secure secret management",
      "cwe": "CWE-798"
    },
    {
      "severity": "critical",
      "type": "command_injection",
      "line": 14,
      "message": "Command injection vulnerability: Unvalidated user input in system command",
      "snippet": "os.system(f\"ping {user_input}\")",
      "recommendation": "Use subprocess.run with shell=False and command list",
      "cwe": "CWE-78"
    },
    {
      "severity": "medium",
      "type": "insecure_deserialization",
      "line": 17,
      "message": "Insecure deserialization of untrusted data",
      "snippet": "pickle.loads(data)",
      "recommendation": "Use secure serialization formats like JSON with schema validation",
      "cwe": "CWE-502"
    }
  ],
  "suggested_fixes": {
    "sql_injection": {
      "old": "query = f\"SELECT * FROM users WHERE id = {user_input}\"",
      "new": "query = \"SELECT * FROM users WHERE id = %s\"\ncursor.execute(query, [user_input])"
    },
    "command_injection": {
      "old": "os.system(f\"ping {user_input}\")",
      "new": "subprocess.run(['ping', user_input], shell=False, check=True)"
    }
  }
}
```

## Test Configurations

### 1. Local Testing Environment

```yaml
# test_config.yaml
environment: test
github:
  token: ${TEST_GITHUB_TOKEN}
  webhook_secret: ${TEST_WEBHOOK_SECRET}
azure_openai:
  endpoint: ${TEST_AZURE_ENDPOINT}
  api_key: ${TEST_AZURE_KEY}
logging:
  level: DEBUG
```

### 2. Test Data Management

```bash
tests/
├── data/
│   ├── pr_payloads/          # Webhook event test data
│   ├── code_samples/         # Test code files
│   └── expected_results/     # Expected analysis outputs
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      
      - name: Run unit tests
        run: pytest tests/unit/
      
      - name: Run integration tests
        run: pytest tests/integration/
        env:
          TEST_GITHUB_TOKEN: ${{ secrets.TEST_GITHUB_TOKEN }}
      
      - name: Run E2E tests
        if: github.event_name == 'push'
        run: pytest tests/e2e/
        env:
          TEST_GITHUB_TOKEN: ${{ secrets.TEST_GITHUB_TOKEN }}
          TEST_WEBHOOK_SECRET: ${{ secrets.TEST_WEBHOOK_SECRET }}
```

## Performance Testing

### 1. Load Testing

```python
# tests/performance/test_load.py
async def test_concurrent_webhooks():
    """Test handling of multiple concurrent webhook events."""
    events = [create_test_event() for _ in range(10)]
    start_time = time.time()
    
    # Send events concurrently
    async with aiohttp.ClientSession() as session:
        tasks = [
            session.post(
                f"{BASE_URL}/webhook",
                json=event,
                headers=get_test_headers()
            )
            for event in events
        ]
        responses = await asyncio.gather(*tasks)
    
    duration = time.time() - start_time
    assert all(r.status == 200 for r in responses)
    assert duration < 5.0  # Should handle 10 events in under 5 seconds
```

### 2. Resource Monitoring

```python
# tests/performance/test_resources.py
def test_memory_usage():
    """Monitor memory usage during analysis."""
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # Run analysis on large PR
    run_large_pr_analysis()
    
    peak_memory = process.memory_info().rss
    assert (peak_memory - initial_memory) < 500 * 1024 * 1024  # Max 500MB increase
```

## Test Coverage Requirements

1. Unit Tests: Minimum 90% coverage
2. Integration Tests: All core flows covered
3. Security Tests: All OWASP Top 10 categories
4. Performance Tests: Response time < 2s for single PR

## Regression Test Suite

The regression suite focuses on previously identified issues:

1. **Rate Limit Handling**
   - Test rapid webhook events
   - Verify backoff strategy
   - Check rate limit headers

2. **Memory Management**
   - Test large PR analysis
   - Monitor memory leaks
   - Verify cleanup

3. **Error Recovery**
   - Test network failures
   - Verify retry mechanisms
   - Check error logging

## Reporting

Test results are available in multiple formats:

1. **JUnit XML**
   ```bash
   pytest --junitxml=test-results.xml
   ```

2. **Coverage Report**
   ```bash
   coverage run -m pytest
   coverage html
   ```

3. **Performance Metrics**
   ```bash
   pytest --benchmark-only
   ```