"""Data models for the PR Reviewer Agent."""
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel

class IssueSeverity(str, Enum):
    """Severity levels for issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUGGESTION = "suggestion"

class Issue(BaseModel):
    """Represents a single issue found during review."""
    severity: IssueSeverity
    message: str
    file_path: str
    line_number: Optional[int]
    code_snippet: Optional[str]
    rule_name: str
    suggested_fix: Optional[str]

class PRContext(BaseModel):
    """Context information about a pull request."""
    pr_number: int
    repository: str
    base_branch: str
    head_branch: str
    files_changed: List[str]
    diff_content: Dict[str, str]
    author: str
    title: str
    description: Optional[str]

class ReviewResult(BaseModel):
    """Results of a PR review."""
    issues: List[Issue]
    summary: str
    review_time: float
    total_files_reviewed: int
    stats: Dict[str, int]  # Various statistics about the review

class AgentStats(BaseModel):
    """Agent statistics."""
    prs_reviewed: int = 0
    issues_found: int = 0
    review_time_avg: float = 0.0
    success_rate: float = 0.0