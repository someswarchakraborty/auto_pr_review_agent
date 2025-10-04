"""Configuration management for the PR Reviewer Agent."""
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import BaseModel, field_validator

# Setup logger
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class InsecureConfig(BaseModel):
    """Insecure configuration pattern and message."""
    pattern: str
    message: str

class SecurityRules(BaseModel):
    """Security rule configurations."""
    sql_injection_patterns: List[str]
    secret_patterns: Dict[str, str]
    insecure_configs: Dict[str, InsecureConfig]

class LayerViolation(BaseModel):
    """Layer violation rule."""
    name: str
    pattern: str
    scope: str
    message: str

class DependencyRule(BaseModel):
    """Dependency rule."""
    name: str
    pattern: str
    message: str
    scope: Optional[str] = None

class PatternViolation(BaseModel):
    """Pattern violation rule."""
    name: str
    pattern: str
    message: str

class ArchitectureRules(BaseModel):
    """Architecture rule configurations."""
    layer_violations: List[LayerViolation]
    dependency_rules: List[DependencyRule]
    pattern_violations: List[PatternViolation]

class ComplexityRules(BaseModel):
    """Code complexity rules."""
    max_cognitive_complexity: int
    max_cyclomatic_complexity: int
    max_parameters: int

class CodingStandardRules(BaseModel):
    """Coding standard rule configurations."""
    max_method_length: int
    max_nesting_depth: int
    naming_conventions: Dict[str, str]
    complexity_rules: ComplexityRules

class Rules(BaseModel):
    """All rule configurations."""
    security: SecurityRules
    architecture: ArchitectureRules
    coding_standards: CodingStandardRules

class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str
    file: str
    format: str
    max_size: str
    backup_count: int

class MCPConfig(BaseModel):
    """MCP integration configuration."""
    endpoint: str = "https://mcp.github.dev/v1"  # Default to GitHub-hosted MCP
    batch_size: int
    timeout: int
    retry: Dict[str, int]

class AzureOpenAIConfig(BaseModel):
    """Azure OpenAI configuration."""
    deployment: str
    temperature: float
    max_tokens: int
    timeout: int

class GithubConfig(BaseModel):
    """GitHub integration configuration."""
    webhook_events: List[str] = ["pull_request", "pull_request_review"]
    required_status_checks: List[str] = ["pr-review", "security-scan"]
    webhook_secret: Optional[str] = None
    api_url: str = "https://api.github.com"  # Default GitHub API URL

class IntegrationsConfig(BaseModel):
    """All integrations configuration."""
    github: GithubConfig
    azure_openai: AzureOpenAIConfig

class AnalysisConfig(BaseModel):
    """Analysis configuration."""
    severity_levels: Dict[str, str]
    prioritization: Dict[str, int]
    ignore_patterns: List[str]

class CacheConfig(BaseModel):
    """Cache configuration."""
    enabled: bool
    ttl: int
    max_size: int

class RateLimitingConfig(BaseModel):
    """Rate limiting configuration."""
    enabled: bool
    max_requests: int
    window_seconds: int

class PerformanceConfig(BaseModel):
    """Performance configuration."""
    cache: CacheConfig
    rate_limiting: RateLimitingConfig

class AgentConfig(BaseSettings):
    """Main configuration for the PR Reviewer Agent."""
    
    # Basic configuration
    environment: str = "development"
    
    # Review settings
    review_timeout: int = 300
    max_files: int = 100
    concurrent_reviews: int = 5
    polling_interval: int = 60
    error_retry_interval: int = 300
    
    # Azure OpenAI Configuration
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_chat_deployment_name: Optional[str] = None
    azure_openai_api_version: str = "2024-02-15-preview"  # Default to latest stable version

    # GitHub Configuration
    github_token: Optional[str] = None
    github_webhook_secret: Optional[str] = None

    # MCP Configuration
    mcp_endpoint: str = "https://mcp.github.dev/v1"  # Default to GitHub-hosted MCP
    monitored_repositories: str = ""  # Changed to str to handle raw env var
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/agent.log"
    
    # Component configurations
    rules: Optional[Rules] = None
    logging: Optional[LoggingConfig] = None
    mcp: Optional[MCPConfig] = None
    analysis: Optional[AnalysisConfig] = None
    performance: Optional[PerformanceConfig] = None
    integrations: Optional[IntegrationsConfig] = None

    model_config = {
        'env_file': '.env',
        'env_file_encoding': 'utf-8',
        'case_sensitive': False,
        'use_enum_values': True,
        'str_strip_whitespace': True,
        'env_prefix': '',  # Allow environment variables without prefix
    }

    @property
    def repository_list(self) -> List[str]:
        """Get the list of monitored repositories."""
        if not self.monitored_repositories:
            return []
        return [r.strip() for r in self.monitored_repositories.split(",") if r.strip()]

    @field_validator("monitored_repositories", mode="before")
    @classmethod
    def validate_repositories(cls, v: Any) -> str:
        """Validate and normalize repository string."""
        if v is None:
            return ""
        if isinstance(v, list):
            return ",".join(str(x).strip() for x in v if str(x).strip())
        return str(v).strip()

def deep_merge(target: Dict, source: Dict) -> Dict:
    """Deep merge two dictionaries."""
    for key, value in source.items():
        if key in target:
            if isinstance(target[key], dict) and isinstance(value, dict):
                deep_merge(target[key], value)
            else:
                target[key] = value
        else:
            target[key] = value
    return target

def load_config(config_path: Optional[str] = None) -> AgentConfig:
    """Load configuration from file and environment variables.
    
    Args:
        config_path: Optional path to the configuration file. If not provided,
                    will look in default locations.
    
    Returns:
        AgentConfig: Configuration instance with loaded settings.
    
    Raises:
        FileNotFoundError: If configuration file cannot be found.
        yaml.YAMLError: If configuration file is invalid YAML.
    """
    # Load environment variables
    load_dotenv()

    # Start with default configuration
    config = get_default_config()
    
    # Find config file if not provided
    if not config_path:
        possible_paths = [
            Path(__file__).parent.parent.parent / "config" / "settings.yaml",  # Root config dir
            Path(__file__).parent.parent / "config" / "settings.yaml",         # src/config
            Path(__file__).parent / "config" / "settings.yaml",               # core/config
            Path("config") / "settings.yaml",                                 # ./config
        ]
        
        for path in possible_paths:
            if path.exists():
                config_path = str(path)
                break
    
    # Load YAML configuration if available
    if config_path:
        try:
            with open(config_path) as f:
                yaml_config = yaml.safe_load(f)
            config = deep_merge(config, yaml_config)
        except FileNotFoundError:
            logger.warning(f"Configuration file not found at {config_path}, using defaults")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise
    
    try:
        # Let Pydantic handle the environment variables and validation
        return AgentConfig(**config)
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise

def get_default_config() -> Dict:
    """Get default configurations."""
    return {
        "environment": "development",
        "review_timeout": 300,
        "max_files": 100,
        "concurrent_reviews": 5,
        "polling_interval": 60,
        "error_retry_interval": 300,
        
        "rules": {
            "security": {
                "sql_injection_patterns": [
                    r"execute\s*\(\s*[\"'].*?\%.*?[\"']",
                    r"raw_connection\s*\(\s*[\"'].*?[\"']"
                ],
                "secret_patterns": {
                    "api_key": r"api[_-]?key.*?['\"]([a-zA-Z0-9]{16,})['\"]",
                    "password": r"password.*?['\"]([^'\"]{8,})['\"]",
                    "token": r"token.*?['\"]([a-zA-Z0-9_-]{8,})['\"]"
                },
                "insecure_configs": {
                    "debug_mode": {
                        "pattern": r"debug\s*=\s*True",
                        "message": "Debug mode enabled in configuration"
                    },
                    "cors_all": {
                        "pattern": r"cors_allow_all\s*=\s*True|[\"']\*[\"']",
                        "message": "Overly permissive CORS configuration"
                    }
                }
            },
            "architecture": {
                "layer_violations": [
                    {
                        "name": "no_db_in_controller",
                        "pattern": r"repository\.|EntityManager\.",
                        "scope": "*/controller/*",
                        "message": "Direct database access in controller layer"
                    },
                    {
                        "name": "no_view_in_service",
                        "pattern": r"render|redirect",
                        "scope": "*/service/*",
                        "message": "View logic in service layer"
                    }
                ],
                "dependency_rules": [
                    {
                        "name": "no_circular_deps",
                        "pattern": r"import.*\.\..*",
                        "message": "Avoid parent directory imports"
                    },
                    {
                        "name": "no_cross_module_deps",
                        "pattern": r"from ..* import",
                        "scope": "*/core/*",
                        "message": "Core modules should not depend on feature modules"
                    }
                ],
                "pattern_violations": [
                    {
                        "name": "use_dependency_injection",
                        "pattern": r"new\s+[A-Z][a-zA-Z0-9]*\(",
                        "message": "Use dependency injection instead of direct instantiation"
                    },
                    {
                        "name": "no_static_utils",
                        "pattern": r"@staticmethod",
                        "message": "Prefer instance methods over static utilities"
                    }
                ]
            },
            "coding_standards": {
                "max_method_length": 50,
                "max_nesting_depth": 4,
                "naming_conventions": {
                    "class": r"^[A-Z][a-zA-Z0-9]*$",
                    "method": r"^[a-z][a-zA-Z0-9]*$",
                    "variable": r"^[a-z][a-zA-Z0-9]*$",
                    "constant": r"^[A-Z][A-Z0-9_]*$"
                },
                "complexity_rules": {
                    "max_cognitive_complexity": 15,
                    "max_cyclomatic_complexity": 10,
                    "max_parameters": 5
                }
            }
        },
        
        "logging": {
            "level": "INFO",
            "file": "logs/agent.log",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "max_size": "10MB",
            "backup_count": 5
        },
        
        "mcp": {
            "endpoint": "https://mcp.github.dev/v1",  # Default to GitHub-hosted MCP
            "batch_size": 10,
            "timeout": 30,
            "retry": {
                "max_attempts": 3,
                "initial_delay": 1,
                "max_delay": 10
            }
        },
        
        "analysis": {
            "severity_levels": {
                "error": "Must be fixed before merge",
                "warning": "Should be addressed",
                "info": "Consider improving",
                "suggestion": "Optional enhancement"
            },
            "prioritization": {
                "security": 1,
                "architecture": 2,
                "style": 3
            },
            "ignore_patterns": [
                "*/test/*",
                "*/generated/*",
                "*/migrations/*",
                "*/vendor/*"
            ]
        },
        
        "performance": {
            "cache": {
                "enabled": True,
                "ttl": 3600,
                "max_size": 1000
            },
            "rate_limiting": {
                "enabled": True,
                "max_requests": 100,
                "window_seconds": 60
            }
        },
        
        "integrations": {
            "github": {
                "webhook_events": [
                    "pull_request",
                    "pull_request_review"
                ],
                "required_status_checks": [
                    "pr-review",
                    "security-scan"
                ],
                "webhook_secret": None,  # Will be overridden by environment variable
                "api_url": "https://api.github.com"  # Default GitHub API URL
            },
            "azure_openai": {
                "deployment": "${AZURE_OPENAI_DEPLOYMENT}",
                "temperature": 0.3,
                "max_tokens": 2000,
                "timeout": 30
            }
        }
    }