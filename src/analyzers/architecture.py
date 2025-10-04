"""Architecture analyzer implementation."""
import re
from typing import List

from src.analyzers.base import BaseAnalyzer
from src.core.models import Issue, IssueSeverity, PRContext

class ArchitectureAnalyzer(BaseAnalyzer):
    """Analyzes code for architectural violations."""

    async def analyze(self, context: PRContext) -> List[Issue]:
        """Analyze PR for architectural violations."""
        issues = []
        rules = self.config.rules.architecture

        for file_path, content in context.diff_content.items():
            for rule in rules:
                violations = self._check_rule(file_path, content, rule)
                issues.extend(violations)

        return issues

    def _check_rule(self, file_path: str, content: str, rule: dict) -> List[Issue]:
        """Check a single architecture rule."""
        issues = []
        
        if not self._file_matches_scope(file_path, rule["scope"]):
            return issues

        pattern = re.compile(rule["pattern"])
        for i, line in enumerate(content.splitlines(), 1):
            if pattern.search(line):
                issues.append(
                    self._create_issue(
                        severity=IssueSeverity.ERROR,
                        message=rule["message"],
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        rule_name=rule["name"]
                    )
                )

        return issues

    def _file_matches_scope(self, file_path: str, scope_pattern: str) -> bool:
        """Check if file matches the rule scope."""
        return bool(re.match(scope_pattern, file_path))