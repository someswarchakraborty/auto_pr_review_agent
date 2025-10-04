"""Text processing utilities for the PR Reviewer Agent."""
import re
from typing import List, Tuple

def extract_code_block(text: str) -> List[Tuple[str, str]]:
    """Extract code blocks and their language from text.

    Args:
        text: Text containing code blocks

    Returns:
        List of tuples (language, code)
    """
    pattern = r"```(\w+)?\n(.*?)```"
    matches = re.finditer(pattern, text, re.DOTALL)
    return [(m.group(1) or "", m.group(2).strip()) for m in matches]

def format_issue_comment(
    severity: str,
    message: str,
    suggestion: str = None,
    code_snippet: str = None
) -> str:
    """Format an issue comment for GitHub.

    Args:
        severity: Issue severity (error, warning, info)
        message: Issue description
        suggestion: Optional suggestion for fixing
        code_snippet: Optional code snippet

    Returns:
        Formatted comment string
    """
    emoji_map = {
        "error": "🔴",
        "warning": "🟡",
        "info": "ℹ️",
        "suggestion": "💡"
    }

    comment = [f"{emoji_map.get(severity.lower(), 'ℹ️')} **{severity.upper()}**: {message}"]
    
    if code_snippet:
        comment.append("\nRelevant code:")
        comment.append(f"```\n{code_snippet}\n```")
    
    if suggestion:
        comment.append("\n💡 **Suggestion**:")
        comment.append(suggestion)
    
    return "\n".join(comment)

def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to specified length while keeping whole words.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
        
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return f"{truncated}..."