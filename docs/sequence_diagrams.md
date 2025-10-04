# Sequence Diagrams

This document provides sequence diagrams showing the key interactions between system components.

## Pull Request Review Flow

![PR Review Flow](diagrams/pr_review_flow.png)

This diagram shows the complete flow of a pull request review from webhook trigger to review completion.

## Analysis Pipeline

![Analysis Pipeline](diagrams/analysis_pipeline_flow.png)

The analysis pipeline flow shows how different analyzers process the code and aggregate results.

## Webhook Processing

![Webhook Processing](diagrams/webhook_processing_details.png)

Detailed flow of webhook processing including signature verification and rate limiting.

## Key Interactions

### 1. Webhook Reception
```mermaid
sequenceDiagram
    participant GitHub
    participant Webhook Handler
    participant Security Validator
    participant Queue

    GitHub->>Webhook Handler: POST /webhook
    Webhook Handler->>Security Validator: Verify Signature
    Security Validator-->>Webhook Handler: Valid/Invalid
    alt signature valid
        Webhook Handler->>Queue: Queue Review Task
        Queue-->>Webhook Handler: Task Queued
        Webhook Handler->>GitHub: 200 OK
    else signature invalid
        Webhook Handler->>GitHub: 401 Unauthorized
    end
```

### 2. Code Analysis
```mermaid
sequenceDiagram
    participant Queue
    participant Agent
    participant Analyzers
    participant GitHub API
    participant OpenAI

    Queue->>Agent: Process Review Task
    Agent->>GitHub API: Fetch PR Details
    GitHub API-->>Agent: PR Content
    
    par Security Analysis
        Agent->>Analyzers: Run Security Check
        Analyzers->>OpenAI: Analyze Security
        OpenAI-->>Analyzers: Security Findings
        Analyzers-->>Agent: Security Report
    and Architecture Analysis
        Agent->>Analyzers: Run Architecture Check
        Analyzers->>OpenAI: Analyze Architecture
        OpenAI-->>Analyzers: Architecture Findings
        Analyzers-->>Agent: Architecture Report
    and Style Analysis
        Agent->>Analyzers: Run Style Check
        Analyzers->>OpenAI: Analyze Style
        OpenAI-->>Analyzers: Style Findings
        Analyzers-->>Agent: Style Report
    end
    
    Agent->>GitHub API: Post Review Comments
    GitHub API-->>Agent: Review Posted
```

### 3. Error Recovery
```mermaid
sequenceDiagram
    participant Agent
    participant Queue
    participant Error Handler
    participant Metrics
    
    Agent->>Error Handler: Exception Occurred
    Error Handler->>Metrics: Log Error
    alt can retry
        Error Handler->>Queue: Requeue Task
        Queue-->>Error Handler: Task Requeued
        Error Handler-->>Agent: Retry Scheduled
    else max retries exceeded
        Error Handler->>Metrics: Log Failure
        Error Handler-->>Agent: Abort Review
    end
```

## Integration Points

The sequence diagrams above highlight several key integration points:

1. **GitHub Integration**
   - Webhook reception and validation
   - API interactions for PR data
   - Review comment posting
   
2. **Azure OpenAI Integration**
   - Code analysis requests
   - Natural language processing
   - Review summary generation
   
3. **Internal System Flow**
   - Task queueing and processing
   - Parallel analysis execution
   - Error handling and recovery

## References

- [Architecture Overview](architecture.md)
- [GitHub Integration Guide](github_integration.md)
- [Troubleshooting Guide](troubleshooting.md)