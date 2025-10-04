"""Security analyzer implementation."""
from typing import List
import re

from .base import BaseAnalyzer
from src.core.models import Issue, IssueSeverity, PRContext

class SecurityAnalyzer(BaseAnalyzer):
    """Analyzes code for security vulnerabilities."""

    async def analyze(self, context: PRContext) -> List[Issue]:
        """Analyze PR for security vulnerabilities."""
        issues = []
        rules = self.config.rules.security

        for file_path, content in context.diff_content.items():
            # Check for common security vulnerabilities
            sql_injection_issues = self._check_sql_injection(file_path, content)
            issues.extend(sql_injection_issues)

            # Check for hardcoded secrets
            secret_issues = self._check_hardcoded_secrets(file_path, content)
            issues.extend(secret_issues)

            # Check for insecure configurations
            config_issues = self._check_insecure_configs(file_path, content)
            issues.extend(config_issues)

        return issues

    def _check_sql_injection(self, file_path: str, content: str) -> List[Issue]:
        """Check for potential SQL injection vulnerabilities."""
        issues = []
        patterns = [
            r"execute\s*\(\s*[\"'].*?\%.*?[\"']",
            r"executemany\s*\(\s*[\"'].*?\%.*?[\"']",
            r"raw_connection\s*\(\s*[\"'].*?[\"']",
            r"cursor\.execute\s*\([^?]*\+",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                issues.append(
                    self._create_issue(
                        severity=IssueSeverity.ERROR,
                        message="Potential SQL injection vulnerability detected",
                        file_path=file_path,
                        line_number=self._get_line_number(content, match.start()),
                        code_snippet=match.group(),
                        rule_name="sql_injection",
                        suggested_fix="Use parameterized queries or an ORM"
                    )
                )

        return issues

    def _check_hardcoded_secrets(self, file_path: str, content: str) -> List[Issue]:
        """Check for hardcoded secrets and credentials."""
        issues = []
        patterns = {
            "api_key": r"api[_-]?key.*?['\"]([a-zA-Z0-9]{16,})['\"]",
            "password": r"password.*?['\"]([^'\"]{8,})['\"]",
            "secret": r"secret.*?['\"]([^'\"]{8,})['\"]",
            "token": r"token.*?['\"]([a-zA-Z0-9_-]{8,})['\"]",
        }

        for secret_type, pattern in patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                issues.append(
                    self._create_issue(
                        severity=IssueSeverity.ERROR,
                        message=f"Hardcoded {secret_type} detected",
                        file_path=file_path,
                        line_number=self._get_line_number(content, match.start()),
                        code_snippet=match.group().replace(match.group(1), "*" * len(match.group(1))),
                        rule_name="hardcoded_secret",
                        suggested_fix="Use environment variables or a secure secret management system"
                    )
                )

        return issues

    def _check_insecure_configs(self, file_path: str, content: str) -> List[Issue]:
        """Check for insecure configuration settings."""
        issues = []
        patterns = {
            "debug_mode": (
                r"debug\s*=\s*True",
                "Debug mode enabled in configuration",
                "Disable debug mode in production environments"
            ),
            "cors_all": (
                r"cors_allow_all\s*=\s*True|[\"']\\*[\"']",
                "Overly permissive CORS configuration",
                "Specify allowed origins explicitly"
            ),
            "ssl_verify": (
                r"verify\s*=\s*False|SSL_VERIFY\s*=\s*False",
                "SSL certificate verification disabled",
                "Enable SSL certificate verification"
            ),
        }

        for check_name, (pattern, message, fix) in patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                issues.append(
                    self._create_issue(
                        severity=IssueSeverity.ERROR,
                        message=message,
                        file_path=file_path,
                        line_number=self._get_line_number(content, match.start()),
                        code_snippet=match.group(),
                        rule_name=f"insecure_config_{check_name}",
                        suggested_fix=fix
                    )
                )

        return issues

    def _get_line_number(self, content: str, pos: int) -> int:
        """Get line number for a position in the content."""
        return content[:pos].count('\n') + 1