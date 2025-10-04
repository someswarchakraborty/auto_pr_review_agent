"""Base analyzer implementation."""
from abc import ABC, abstractmethod
from typing import List

from src.core.models import Issue, PRContext

class BaseAnalyzer(ABC):
    """Base class for all analyzers."""

    def __init__(self, config):
        """Initialize analyzer with configuration."""
        self.config = config

    @abstractmethod
    async def analyze(self, context: PRContext) -> List[Issue]:
        """Analyze the PR and return found issues."""
        pass

    def _create_issue(self, **kwargs) -> Issue:
        """Helper method to create an Issue instance."""
        return Issue(**kwargs)