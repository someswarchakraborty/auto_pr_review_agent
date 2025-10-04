from pyngrok import ngrok, conf
import time
import logging
import os
import signal
import sys
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def cleanup_ngrok():
    """Clean up any existing ngrok processes."""
    try:
        ngrok.kill()
        time.sleep(2)  # Give it time to clean up
    except Exception as e:
        logger.warning(f"Error during ngrok cleanup: {e}")

def setup_webhook_tunnel(port: int = 8000) -> Optional[str]:
    """Set up ngrok tunnel for webhook testing.
    
    Args:
        port: The local port to tunnel to (default: 8000)
        
    Returns:
        The webhook URL if successful, None otherwise
    """
    cleanup_ngrok()
    
    try:
        # Configure ngrok
        conf.get_default().region = 'us'  # Set region explicitly
        
        # Start ngrok tunnel
        logger.info(f"Starting ngrok tunnel on port {port}...")
        public_url = ngrok.connect(port, "http")
        webhook_url = f"{public_url}/webhook"
        
        # Print setup instructions
        print("\n=== GitHub Webhook Setup Instructions ===")
        print(f"\n1. Webhook URL to use: {webhook_url}")
        print("\n2. Go to your repository settings:")
        print("   https://github.com/someswarchakraborty/auto_pr_review_agent/settings/hooks")
        print("\n3. Click 'Edit' on the existing webhook or 'Add webhook' and enter:")
        print("   - Payload URL:", webhook_url)
        print("   - Content type: application/json")
        print("   - Secret: [Your webhook secret from .env file]")
        print("\n4. Under 'Which events would you like to trigger this webhook?':")
        print("   - Select 'Let me select individual events'")
        print("   - Check 'Pull requests' and 'Pull request reviews'")
        print("\n5. Make sure 'Active' is checked")
        print("\n6. Click 'Update webhook' or 'Add webhook'")
        print("\nThe tunnel is now running. Press Ctrl+C to stop.")
        
        def signal_handler(signum, frame):
            """Handle shutdown signals."""
            logger.info("\nReceived shutdown signal. Cleaning up...")
            cleanup_ngrok()
            sys.exit(0)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Keep the script running and monitor tunnel status
        while True:
            tunnels = ngrok.get_tunnels()
            if not tunnels:
                logger.error("Tunnel disconnected! Attempting to reconnect...")
                public_url = ngrok.connect(port, "http")
            time.sleep(5)
            
    except KeyboardInterrupt:
        logger.info("\nShutting down ngrok tunnel...")
        cleanup_ngrok()
        
    except Exception as e:
        logger.error(f"Error setting up ngrok tunnel: {str(e)}")
        cleanup_ngrok()
        raise
        
    return webhook_url

if __name__ == "__main__":
    setup_webhook_tunnel()