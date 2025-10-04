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
- Real-time code analysis and feedback
- Security vulnerability scanning
- Architecture compliance verification
- Best practices enforcement
- Intelligent code improvement suggestions
- Natural language summary generation

### Advanced Capabilities
- Multi-repository support
- Configurable analysis rules
- Custom review policies
- Automatic retries and error recovery
- Webhook signature verification
- Detailed logging and monitoring
- Rate limit handling

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
- Webhook handler with signature verification
- Async code analysis pipeline
- GitHub API integration client
- Configuration management system
- Logging and monitoring system

## Documentation

- [Setup Guide](docs/setup.md) - Installation and configuration guide
- [Usage Guide](docs/usage.md) - How to use the PR Reviewer Agent
- [Configuration Guide](docs/configuration.md) - Configuration options and settings
- [Architecture Overview](docs/architecture.md) - System design and components
- [GitHub Integration](docs/github_integration.md) - GitHub API and webhook integration
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

## Environment Variables

The following environment variables are required:

- `GITHUB_TOKEN` - GitHub Personal Access Token
- `OPENAI_API_KEY` - Azure OpenAI API Key
- `OPENAI_API_BASE` - Azure OpenAI API Base URL
- `WEBHOOK_SECRET` - GitHub webhook secret for verification
- `NGROK_TOKEN` - (Optional) ngrok authentication token for local development

See `example.env` for a complete list of configuration options.

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