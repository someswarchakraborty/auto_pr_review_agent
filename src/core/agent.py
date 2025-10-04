"""Core agent implementation using LangChain and MCP."""
from typing import Dict, List, Optional
import asyncio
import logging
import sys
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from langchain.agents import AgentExecutor, Tool, create_openai_functions_agent
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.tools import BaseTool
from pydantic import BaseModel

from src.analyzers.architecture import ArchitectureAnalyzer
from src.analyzers.code_style import CodeStyleAnalyzer
from src.analyzers.security import SecurityAnalyzer
from src.core.config import AgentConfig
from src.core.models import PRContext, ReviewResult
from src.utils.mcp import MCPClient
from src.utils.logging import get_logger

logger = get_logger(__name__)

class PRReviewerAgent:
    """Main agent class for PR review automation."""

    def __init__(self, config: AgentConfig):
        """Initialize the agent with configuration."""
        self.config = config
        self.running = False
        
        # Initialize components in correct order
        self._setup_analyzers()  # Must be first as tools depend on analyzers
        self.tools = self._setup_tools()
        self.executor = self._setup_executor()
        
        # Initialize MCP client with GitHub token and API URL
        self.mcp_client = MCPClient(
            base_url=config.mcp_endpoint,
            github_token=config.github_token,
            github_api_url=config.integrations.github.api_url if config.integrations and config.integrations.github else "https://api.github.com"
        )
        
        # Initialize statistics
        self.stats = {"prs_reviewed": 0, "issues_found": 0}

    def _setup_analyzers(self):
        """Initialize code analyzers."""
        self.architecture_analyzer = ArchitectureAnalyzer(self.config)
        self.style_analyzer = CodeStyleAnalyzer(self.config)
        self.security_analyzer = SecurityAnalyzer(self.config)

    def _setup_tools(self) -> List[BaseTool]:
        """Set up LangChain tools for the agent."""
        return [
            Tool(
                name="analyze_architecture",
                func=self.architecture_analyzer.analyze,
                description="Analyze code for architectural violations"
            ),
            Tool(
                name="analyze_style",
                func=self.style_analyzer.analyze,
                description="Check code style and standards"
            ),
            Tool(
                name="analyze_security",
                func=self.security_analyzer.analyze,
                description="Check for security vulnerabilities"
            ),
        ]

    def _setup_executor(self) -> AgentExecutor:
        """Set up the LangChain agent executor."""
        from langchain.chat_models import AzureChatOpenAI
        from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain.schema import SystemMessage
        from langchain.agents import OpenAIFunctionsAgent
        
        # Initialize Azure OpenAI chat model
        llm = AzureChatOpenAI(
            deployment_name=self.config.azure_openai_chat_deployment_name,
            temperature=0.1,
            azure_endpoint=self.config.azure_openai_endpoint,
            api_key=self.config.azure_openai_api_key,            
            openai_api_version=self.config.azure_openai_api_version,
            max_tokens=2000           
        )
        
        # Create the agent prompt
        system_message = SystemMessage(
            content="""You are a code review assistant that helps analyze pull requests.
            Your goal is to identify issues and suggest improvements in the code.
            Be thorough but constructive in your feedback."""
        )
        
        prompt = ChatPromptTemplate.from_messages([
            system_message,
            MessagesPlaceholder(variable_name="chat_history"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Initialize the agent using the recommended create_openai_functions_agent method
        from langchain.agents import create_openai_functions_agent
        agent = create_openai_functions_agent(
            llm=llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create and return the agent executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            early_stopping_method="generate",
            handle_parsing_errors=True
        )

    async def start(self):
        """Start the agent."""
        self.running = True
        # Start monitoring PRs
        asyncio.create_task(self._monitor_prs())

    async def stop(self):
        """Stop the agent."""
        self.running = False

    async def _monitor_prs(self):
        """Monitor for new PRs using MCP."""
        while self.running:
            try:
                # Get PR updates through MCP
                # Convert comma-separated string to list
                repositories = [repo.strip() for repo in self.config.monitored_repositories.split(',') if repo.strip()]
                prs = await self.mcp_client.get_pending_reviews(
                    repositories=repositories
                )
                
                # Process each PR
                for pr in prs:
                    try:
                        # Get PR context through MCP
                        pr_context = await self.mcp_client.get_pr_context(pr)
                        
                        # Review the PR
                        review_result = await self.review_pr(pr_context)
                        
                        # Post review comments through MCP
                        await self.mcp_client.post_review(
                            pr_context.repository,
                            pr_context.pr_number,
                            review_result
                        )
                        
                        logger.info(f"Completed review for PR #{pr_context.pr_number}")
                    
                    except Exception as e:
                        logger.error(f"Error reviewing PR: {e}")
                
                # Wait for next polling interval
                await asyncio.sleep(self.config.polling_interval)
            
            except Exception as e:
                logger.error(f"Error in PR monitoring: {e}")
                await asyncio.sleep(self.config.error_retry_interval)

    async def review_pr(self, pr_context: PRContext) -> ReviewResult:
        """Review a pull request."""
        try:
            # Get MCP analysis first
            mcp_issues = await self.mcp_client.analyze_pull_request(pr_context)
            
            # Run local analyzers in parallel
            local_results = await asyncio.gather(
                self.architecture_analyzer.analyze(pr_context),
                self.style_analyzer.analyze(pr_context),
                self.security_analyzer.analyze(pr_context)
            )
            
            # Combine MCP and local results
            all_issues = mcp_issues + [
                issue
                for result in local_results
                for issue in result
            ]
            
            # Generate summary using LLM
            summary = await self._generate_summary(all_issues)
            
            return ReviewResult(
                issues=all_issues,
                summary=summary,
                review_time=None,  # Will be set by caller
                total_files_reviewed=len(pr_context.files_changed),
                stats={
                    "mcp_issues": len(mcp_issues),
                    "local_issues": len(all_issues) - len(mcp_issues),
                    "files_analyzed": len(pr_context.files_changed)
                }
            )
            
        except Exception as e:
            logger.error(f"Error during PR review: {e}")
            raise

    async def _generate_summary(self, results: Dict) -> str:
        """Generate natural language summary of review results."""
        # Use Azure OpenAI to generate summary
        # Implementation details here
        pass

    async def get_status(self) -> Dict:
        """Get current agent status."""
        return {
            "running": self.running,
            "prs_reviewed": self.stats.prs_reviewed,
            "issues_found": self.stats.issues_found
        }