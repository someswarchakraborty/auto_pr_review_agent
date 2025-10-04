# PR Reviewer Agent

An intelligent agent that automatically reviews Pull Requests using FastAPI, Azure OpenAI, and GitHub integration. The agent provides comprehensive code review feedback focusing on security, architecture, and best practices.

## Overview

The PR Reviewer Agent is an automated code review system that analyzes pull requests in real-time. It integrates directly with GitHub through webhooks and the GitHub API to provide instant feedback on code changes.

### Key Analysis Areas:
- Security vulnerabilities and code smells
- Architectural pattern compliance
- Coding standards and best practices
- API usage and implementation patterns
- Documentation completeness
- Test coverage and quality

## Features

### Core Features
- Automated PR review triggering via webhooks
- Real-time code analysis and feedback using Model Context Protocol (MCP)
- Security vulnerability scanning with context-aware analysis
- Architecture compliance verification through MCP models
- Best practices enforcement with customizable rules
- Intelligent code improvement suggestions using AI models
- Natural language summary generation via MCP

### Advanced Capabilities
- Model Context Protocol (MCP) integration for enhanced AI analysis
- Multi-repository support with context preservation
- Configurable analysis rules and model parameters
- Custom review policies with MCP-based decision making
- Automatic retries and error recovery with state management
- Webhook signature verification for security
- Detailed logging and monitoring with MCP request tracing
- Rate limit handling for API and model calls
- Context-aware code analysis using MCP memory system

## Technical Stack

### Core Technologies
- Python 3.13+
- FastAPI for webhook handling
- Azure OpenAI for code analysis
- GitHub API for repository integration
- ngrok for local development
- Docker for containerization
- PyTest for testing

### Key Components
- FastAPI application server
- MCP client for context-aware AI analysis
- Webhook handler with signature verification
- Async code analysis pipeline with MCP integration
- GitHub API integration client
- Intelligent context management system
- Configuration management system
- Logging and monitoring system with MCP tracing

## Model Context Protocol (MCP)

The PR Reviewer Agent leverages the Model Context Protocol (MCP) for enhanced code analysis and review capabilities. MCP provides:

1. **Context-Aware Analysis**
   - Maintains conversation history across API calls
   - Preserves code context for better understanding
   - Enables more accurate and consistent reviews

2. **Intelligent Memory Management**
   - Automatically manages context window size
   - Prioritizes relevant information
   - Optimizes token usage

3. **Advanced AI Features**
   - Multi-step reasoning for complex code analysis
   - Pattern recognition across multiple files
   - Learning from previous reviews
   - Contextual code suggestions

4. **Integration Benefits**
   - Improved code understanding
   - More accurate vulnerability detection
   - Better architectural analysis
   - Context-aware suggestions
   - Consistent review style

For detailed MCP configuration and usage, see the [MCP Integration Guide](docs/mcp_integration.md).

## Documentation

- [Setup Guide](docs/setup.md) - Installation and configuration guide
- [Usage Guide](docs/usage.md) - How to use the PR Reviewer Agent
- [Configuration Guide](docs/configuration.md) - Configuration options and settings
- [Architecture Overview](docs/architecture.md) - System design and components
- [GitHub Integration](docs/github_integration.md) - GitHub API and webhook integration
- [MCP Integration Guide](docs/mcp_integration.md) - Model Context Protocol setup and usage
- [Sequence Diagrams](docs/sequence_diagrams.md) - System interaction flows
- [Testing Guide](docs/testing.md) - Testing strategy and procedures
- [Best Practices](docs/best_practices.md) - Development and usage guidelines
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions
- [Contributing Guide](docs/contributing.md) - How to contribute to the project

## Project Structure

```
auto_pr_review_agent/
├── src/
│   ├── __init__.py
│   ├── main.py                # FastAPI application entry point
│   ├── analyzers/             # Code analysis modules
│   │   ├── __init__.py
│   │   ├── architecture.py    # Architecture pattern analysis
│   │   ├── base.py           # Base analyzer class
│   │   ├── code_style.py     # Code style checking
│   │   └── security.py       # Security vulnerability detection
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   ├── agent.py          # PR Review Agent implementation
│   │   ├── config.py         # Configuration management
│   │   └── models.py         # Data models
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── github.py         # GitHub API client
│       ├── logging.py        # Logging configuration
│       ├── metrics.py        # Performance metrics
│       └── text.py           # Text processing utilities
├── scripts/
│   └── setup_tunnel.py       # ngrok tunnel management
├── tests/
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
├── docs/                     # Documentation
│   ├── architecture.md
│   ├── setup.md
│   ├── usage.md
│   └── ...
├── config/                   # Configuration files
│   └── settings.yaml
├── Dockerfile               # Container configuration
├── requirements.txt         # Python dependencies
└── README.md
```

## Quick Start

1. Clone the repository
2. Copy `example.env` to `.env` and configure your environment variables
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   python src/main.py
   ```

## Azure OpenAI Integration

The PR Reviewer Agent uses Azure OpenAI's powerful language models at several key points in the review process:

### 1. Code Analysis
- **Security Analysis** (`src/analyzers/security.py`):
  - Identifies potential security vulnerabilities
  - Analyzes authentication and authorization patterns
  - Detects common security anti-patterns
  - Reviews dependency security

- **Architecture Analysis** (`src/analyzers/architecture.py`):
  - Evaluates architectural patterns
  - Checks design principles compliance
  - Assesses component interactions
  - Reviews system scalability aspects

- **Code Style Analysis** (`src/analyzers/code_style.py`):
  - Reviews code formatting and style
  - Checks naming conventions
  - Evaluates code organization
  - Assesses code readability

### 2. Natural Language Processing
- **Review Summary Generation**:
  - Creates concise PR summaries
  - Highlights key changes
  - Identifies impact areas
  - Provides overall assessment

- **Documentation Analysis**:
  - Reviews documentation completeness
  - Checks API documentation
  - Validates code comments
  - Assesses technical writing quality

### 3. Smart Feedback Generation
- **Context-Aware Suggestions**:
  - Provides specific improvement recommendations
  - Suggests code optimizations
  - Offers alternative implementations
  - Explains the reasoning behind suggestions

### 4. Test Coverage Analysis
- **Test Quality Assessment**:
  - Evaluates test coverage
  - Reviews test patterns
  - Suggests missing test cases
  - Assesses edge case handling

### Azure OpenAI Model Usage
- Uses `gpt-4` or `gpt-35-turbo` based on configuration
- Implements intelligent context management
- Handles rate limiting and retries
- Optimizes token usage for cost efficiency

The integration is handled through the Azure OpenAI REST API, with configurations managed in `config/settings.yaml` and environment variables.

## Environment Variables

The following environment variables are required:

- `GITHUB_TOKEN` - GitHub Personal Access Token
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API Key
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI API Base URL
- `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` - Azure OpenAI gpt model deployment version
- `AZURE_OPENAI_API_VERSION` - Azure OpenAI API version
- `WEBHOOK_SECRET` - GitHub webhook secret for verification
- `NGROK_TOKEN` - (Optional) ngrok authentication token for local development
-  For GitHub MCP we do need any separate MCP env variable or configuration


## Setup Instructions

Detailed setup instructions can be found in [docs/setup.md](docs/setup.md)

## Configuration

Configuration details are available in [docs/configuration.md](docs/configuration.md)

## Usage

Usage instructions can be found in [docs/usage.md](docs/usage.md)

## Contributing

Please read [docs/contributing.md](docs/contributing.md) for contribution guidelines.

## License

MIT License - See LICENSE file for details