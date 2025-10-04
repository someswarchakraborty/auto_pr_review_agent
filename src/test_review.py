"""Test module for PR review with additional security and architecture issues."""
import os
import sqlite3
import json
import base64
from typing import Any, Dict, List, Optional

def insecure_database_operation(user_input: str) -> List[Dict[str, Any]]:
    """This function has multiple issues for the PR reviewer to find."""
    # Security issue: SQL injection vulnerability
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Intentional SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{user_input}'"
    cursor.execute(query)
    
    # Resource management issue: not closing connection
    return cursor.fetchall()

def complex_function(a: int, b: int, c: int, d: int, e: int, f: int) -> int:
    """This function has complexity and maintainability issues."""
    # Too many parameters and high cyclomatic complexity
    result = 0
    
    # Nested conditions creating high cognitive complexity
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        result = f
                    else:
                        result = e
                else:
                    result = d
            else:
                result = c
        else:
            result = b
    else:
        result = a
        
    return result

class UtilityClass:
    """Class with multiple architectural and security issues."""
    
    def __init__(self):
        """Initialize with hardcoded credentials - security issue."""
        self.api_key = "sk_live_123456789abcdef"  # Security: Hardcoded API key
        self.debug_mode = True  # Security: Debug mode enabled in production
    
    @staticmethod
    def helper_method() -> str:
        """Static utility method that should be instance method."""
        return "helper"
    
    def process_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Method with multiple issues."""
        if self.debug_mode:
            # Security: Logging sensitive data
            print(f"API Key: {self.api_key}")
            print(f"Processing data: {json.dumps(data, indent=2)}")
            
        # Architecture issue: Direct database access in wrong layer
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM data")
        
        # Security issue: Storing sensitive data in plaintext
        with open('temp_data.txt', 'w') as f:
            f.write(base64.b64encode(str(data).encode()).decode())
        
        return cursor.fetchall()

    def unsafe_file_operation(self, filename: str) -> None:
        """Method with path traversal vulnerability."""
        # Security issue: Path traversal vulnerability
        with open(f"data/{filename}", 'r') as f:
            content = f.read()
            
        # Security issue: Command injection vulnerability
        os.system(f"process_file {filename}")  # nosec