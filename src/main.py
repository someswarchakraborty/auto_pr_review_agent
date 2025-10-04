"""Main entry point for the PR Reviewer Agent."""
import asyncio
import hashlib
import hmac
import json
import logging
import sys
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from pydantic_settings import BaseSettings

from src.core.agent import PRReviewerAgent
from src.core.config import load_config
from src.utils.logging import setup_logging


# Initialize FastAPI app
app = FastAPI(title="PR Reviewer Agent")

# Load configuration
config = load_config()

# Setup logging
logger = logging.getLogger(__name__)

# Initialize the agent
agent = PRReviewerAgent(config)

@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    logger.info("Starting PR Reviewer Agent")
    await agent.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down PR Reviewer Agent")
    await agent.stop()

@app.get("/status")
async def get_status():
    """Get agent status."""
    return await agent.get_status()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/webhook")
async def github_webhook(request: Request):
    """Handle GitHub webhook events."""
    try:
        # Log incoming webhook request
        logger.info(f"Received webhook request from {request.client.host}")
        logger.debug(f"Headers: {dict(request.headers)}")
        
        body = await request.body()
        event_type = request.headers.get("X-GitHub-Event")
        delivery_id = request.headers.get("X-GitHub-Delivery", "unknown")
        
        logger.info(f"Processing GitHub webhook event: {event_type} (ID: {delivery_id})")
        
        # Verify webhook signature if secret is configured
        if (config.integrations and config.integrations.github and 
            config.integrations.github.webhook_secret):
            signature = request.headers.get("X-Hub-Signature-256")
            if not signature:
                logger.error(f"No signature provided for event {delivery_id}")
                raise HTTPException(status_code=400, detail="No signature provided")
            
            # Verify webhook secret
            secret = config.integrations.github.webhook_secret.encode()
            expected_signature = "sha256=" + hmac.new(
                secret,
                msg=body,
                digestmod=hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                logger.error(f"Invalid signature for event {delivery_id}")
                raise HTTPException(status_code=401, detail="Invalid signature")
            
            logger.debug(f"Webhook signature verified for event {delivery_id}")
        else:
            logger.warning("Webhook secret not configured - skipping signature verification")
        
        # Parse the event data
        try:
            event_data = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse webhook payload for event {delivery_id}: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Validate event type
        event_types = (config.integrations.github.webhook_events 
                      if config.integrations and config.integrations.github 
                      else ["pull_request", "pull_request_review"])
                      
        if event_type not in event_types:
            logger.info(f"Ignoring unhandled event type: {event_type} (ID: {delivery_id})")
            return {
                "status": "ignored",
                "reason": f"Event type {event_type} not configured for processing",
                "delivery_id": delivery_id
            }
        
        # Validate repository
        if 'repository' in event_data:
            repo_full_name = event_data['repository']['full_name']
            if repo_full_name not in config.repository_list:
                logger.info(f"Ignoring event from unmonitored repository: {repo_full_name} (ID: {delivery_id})")
                return {
                    "status": "ignored",
                    "reason": f"Repository {repo_full_name} not in monitored list",
                    "delivery_id": delivery_id
                }
            logger.info(f"Processing event for repository: {repo_full_name}")
        
        # Process the event
        try:
            await agent.handle_github_event(event_type, event_data)
            logger.info(f"Successfully processed event {delivery_id}")
            return {
                "status": "processing",
                "delivery_id": delivery_id,
                "event_type": event_type,
                "repository": event_data.get('repository', {}).get('full_name')
            }
        except Exception as e:
            logger.error(f"Error processing event {delivery_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error processing webhook: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error processing webhook", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

def main():
    """Main entry point."""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if config.environment == "development" else False,
    )

if __name__ == "__main__":
    main()