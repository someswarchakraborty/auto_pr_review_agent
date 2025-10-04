"""Security test module for PR review with various security vulnerabilities."""
import os
import subprocess
import pickle
import base64
from typing import Any, Dict, Optional
import yaml

class UserAuthentication:
    """Class demonstrating various security anti-patterns."""
    
    def __init__(self):
        """Initialize with insecure defaults."""
        # Security Issue: Hardcoded credentials
        self.admin_password = "admin123!"
        self.secret_key = "my_super_secret_key_123"
        self.debug = True
        
        # Security Issue: Insecure permissions
        os.chmod("config.yaml", 0o777)
    
    def verify_password(self, username: str, password: str) -> bool:
        """Verify user password with multiple vulnerabilities."""
        # Security Issue: SQL Injection vulnerability
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        
        # Security Issue: Command Injection vulnerability
        result = subprocess.run(
            f"grep '{username}' /etc/passwd",
            shell=True,
            capture_output=True
        )
        
        # Security Issue: Hardcoded backdoor
        if username == "admin" and password == self.admin_password:
            return True
            
        return False

    def load_user_data(self, data: str) -> Dict[str, Any]:
        """Load user data with security issues."""
        # Security Issue: Unsafe deserialization
        return pickle.loads(base64.b64decode(data))
    
    def validate_file_path(self, filepath: str) -> Optional[str]:
        """Validate file path with security vulnerability."""
        # Security Issue: Path traversal vulnerability
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return f.read()
        return None

    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration with YAML vulnerability."""
        # Security Issue: Unsafe YAML loading
        with open(config_file, 'r') as f:
            return yaml.load(f, Loader=yaml.Loader)

    def execute_command(self, cmd: str) -> str:
        """Execute system command with security issues."""
        # Security Issue: Command injection vulnerability
        result = os.system(cmd)
        
        # Security Issue: Information exposure
        if self.debug:
            print(f"Command executed with secret key: {self.secret_key}")
            print(f"Result: {result}")
        
        return str(result)

class InsecureAPI:
    """Class demonstrating API security issues."""
    
    def __init__(self):
        """Initialize with insecure API configuration."""
        # Security Issue: Insecure SSL/TLS configuration
        self.verify_ssl = False
        self.allow_all_origins = True
        
        # Security Issue: Hardcoded API keys
        self.api_keys = {
            "prod": "sk_live_12345abcdef",
            "test": "sk_test_67890ghijkl"
        }
    
    def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle API request with security vulnerabilities."""
        # Security Issue: Sensitive data logging
        print(f"Processing request with API key: {self.api_keys['prod']}")
        
        # Security Issue: No input validation
        user_input = request_data.get('command', '')
        
        # Security Issue: Unsafe eval
        result = eval(user_input)
        
        return {
            "result": result,
            "debug_info": {
                "api_key": self.api_keys['prod'],  # Security Issue: Sensitive data exposure
                "internal_state": str(self.__dict__)
            }
        }

    def generate_token(self, user_id: str) -> str:
        """Generate authentication token with vulnerabilities."""
        # Security Issue: Weak encryption
        return base64.b64encode(f"{user_id}:{self.api_keys['prod']}".encode()).decode()
    
    def validate_token(self, token: str) -> bool:
        """Validate token with security issues."""
        # Security Issue: Timing attack vulnerability
        expected = self.generate_token("admin")
        return token == expected  # Vulnerable to timing attacks