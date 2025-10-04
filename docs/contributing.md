# Contributing Guide

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a new branch for your feature/fix

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- Azure OpenAI API access
- GitHub account with repository access

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -r requirements.txt
```

3. Set up pre-commit hooks:
```bash
pre-commit install
```

4. Create a `.env.local` file for development:
```env
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
GITHUB_TOKEN=your_github_token
```

## Code Style

We follow these coding standards:
- PEP 8 for Python code style
- Type hints for all function parameters and return values
- Docstrings for all modules, classes, and functions
- Maximum line length of 88 characters (using Black formatter)

## Testing

### Running Tests

```bash
pytest tests/
```

### Writing Tests

1. Create test files in the `tests/` directory
2. Use descriptive test names that explain the behavior being tested
3. Include both positive and negative test cases
4. Mock external dependencies appropriately

Example test:
```python
def test_architecture_analyzer_detects_db_in_controller():
    analyzer = ArchitectureAnalyzer(config)
    code = '''
    class UserController:
        def get_user(self):
            return db.query(User).first()
    '''
    issues = analyzer.analyze(code)
    assert len(issues) == 1
    assert issues[0].rule_name == "no_db_in_controller"
```

## Adding New Features

### Adding a New Analyzer

1. Create a new file in `src/analyzers/`
2. Inherit from `BaseAnalyzer`
3. Implement the `analyze` method
4. Add configuration in `settings.yaml`
5. Register the analyzer in `agent.py`

Example:
```python
from .base import BaseAnalyzer

class NewAnalyzer(BaseAnalyzer):
    async def analyze(self, context: PRContext) -> List[Issue]:
        issues = []
        # Implementation here
        return issues
```

### Adding New Rules

1. Define the rule in `settings.yaml`:
```yaml
rules:
  new_category:
    - name: "rule_name"
      pattern: "regex_pattern"
      message: "Rule violation message"
```

2. Implement rule checking in appropriate analyzer

## Pull Request Guidelines

1. Create a descriptive PR title
2. Fill out the PR template
3. Include test coverage for new code
4. Update documentation as needed
5. Ensure CI passes
6. Request review from maintainers

## Release Process

1. Update version in `__version__.py`
2. Update CHANGELOG.md
3. Create a release PR
4. After merge, tag the release
5. Create GitHub release

## Documentation

### Updating Docs

1. All documentation is in Markdown format
2. Place files in the `docs/` directory
3. Update table of contents when adding new pages
4. Include code examples where appropriate

### Documentation Style

- Use clear, concise language
- Include practical examples
- Maintain consistent formatting
- Link related topics
- Keep code examples up to date