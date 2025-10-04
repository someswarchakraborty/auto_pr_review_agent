"""Code style analyzer implementation."""
from typing import List
import re

from .base import BaseAnalyzer
from src.core.models import Issue, IssueSeverity, PRContext

# Optional: Import LLM components if needed
# from langchain.chat_models import AzureChatOpenAI
# from langchain.prompts import PromptTemplate

class CodeStyleAnalyzer(BaseAnalyzer):
    """Analyzes code for style violations."""

    async def analyze(self, context: PRContext) -> List[Issue]:
        """Analyze PR for code style violations."""
        issues = []
        rules = self.config.rules.coding_standards

        for file_path, content in context.diff_content.items():
            # Check method length
            method_issues = self._check_method_length(file_path, content)
            issues.extend(method_issues)

            # Check naming conventions
            naming_issues = self._check_naming_conventions(file_path, content)
            issues.extend(naming_issues)

            # Check code complexity
            complexity_issues = self._check_complexity(file_path, content)
            issues.extend(complexity_issues)

        return issues

    def _check_method_length(self, file_path: str, content: str) -> List[Issue]:
        """Check for methods that exceed maximum length."""
        issues = []
        max_length = self.config.rules.coding_standards.max_method_length
        
        # Simple method detection (can be improved based on language)
        method_pattern = r"(def|function|public|private|protected)\s+\w+\s*\([^)]*\)\s*\{?"
        current_method = None
        line_count = 0
        
        for i, line in enumerate(content.splitlines(), 1):
            if re.search(method_pattern, line):
                if current_method and line_count > max_length:
                    issues.append(
                        self._create_issue(
                            severity=IssueSeverity.WARNING,
                            message=f"Method exceeds maximum length of {max_length} lines",
                            file_path=file_path,
                            line_number=i - line_count,
                            rule_name="max_method_length",
                            suggested_fix="Consider breaking down the method into smaller functions"
                        )
                    )
                current_method = line
                line_count = 1
            elif current_method:
                line_count += 1

        return issues

    def _check_naming_conventions(self, file_path: str, content: str) -> List[Issue]:
        """Check naming conventions."""
        issues = []
        conventions = {
            "class": r"class\s+([a-z][a-zA-Z0-9]*)",
            "method": r"(def|function)\s+([A-Z][a-zA-Z0-9]*)",
            "variable": r"([A-Z][a-zA-Z0-9]*)\s*="
        }

        for conv_type, pattern in conventions.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                issues.append(
                    self._create_issue(
                        severity=IssueSeverity.WARNING,
                        message=f"Invalid {conv_type} name convention",
                        file_path=file_path,
                        line_number=self._get_line_number(content, match.start()),
                        rule_name="naming_convention",
                        suggested_fix=f"Follow {conv_type} naming convention"
                    )
                )

        return issues

    def _check_complexity(self, file_path: str, content: str) -> List[Issue]:
        """Check code complexity metrics."""
        issues = []
        
        # Check nesting depth
        max_depth = self.config.rules.coding_standards.max_nesting_depth
        current_depth = 0
        
        for i, line in enumerate(content.splitlines(), 1):
            indent_level = len(line) - len(line.lstrip())
            depth = indent_level // 4  # Assuming 4 spaces per indent level
            
            if depth > max_depth:
                issues.append(
                    self._create_issue(
                        severity=IssueSeverity.WARNING,
                        message=f"Code nesting depth exceeds maximum of {max_depth}",
                        file_path=file_path,
                        line_number=i,
                        rule_name="max_nesting_depth",
                        suggested_fix="Consider restructuring to reduce nesting"
                    )
                )

        return issues

    def _get_line_number(self, content: str, pos: int) -> int:
        """Get line number for a position in the content."""
        return content[:pos].count('\n') + 1