# PR Reviewer Agent

An intelligent agent that automatically reviews Pull Requests using LangChain, Azure OpenAI, and GitHub MCP integration.

## Overview

The PR Reviewer Agent automates the code review process by analyzing pull requests for:
- Coding standards compliance
- Security vulnerabilities and code smells
- Architectural pattern violations
- API usage and best practices

## Features

- Automatic PR review triggering
- Code analysis and standard verification
- Security vulnerability detection
- Architecture compliance checking
- Intelligent improvement suggestions
- Natural language summary generation

## Technical Stack

- Python 3.11+
- LangChain for agent orchestration
- Azure OpenAI for LLM capabilities
- GitHub MCP for PR integration
- FastAPI for API endpoints
- Docker for containerization

## Documentation

- [Setup Guide](docs/setup.md) - Getting started with installation and configuration
- [Usage Guide](docs/usage.md) - How to use the PR Reviewer Agent
- [Configuration Guide](docs/configuration.md) - Detailed configuration options
- [Architecture Overview](docs/architecture.md) - System design and components
- [MCP Integration Guide](docs/mcp_integration.md) - Working with GitHub MCP
- [Best Practices](docs/best_practices.md) - Recommended practices and patterns
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions
- [Contributing Guide](docs/contributing.md) - How to contribute to the project

## Project Structure

```
pr-reviewer-agent/
├── src/
│   ├── agents/             # Agent implementations
│   ├── analyzers/          # Code analysis modules
│   ├── config/             # Configuration management
│   ├── core/              # Core functionality
│   ├── models/            # Data models
│   └── utils/             # Utility functions
├── tests/                 # Test suite
├── docs/                  # Documentation
└── docker/               # Docker configuration
```

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