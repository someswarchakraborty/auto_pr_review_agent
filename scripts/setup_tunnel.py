from pyngrok import ngrok
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_webhook_tunnel(port=8000):
    """Set up ngrok tunnel for webhook testing."""
    try:
        # Start ngrok tunnel
        logger.info(f"Starting ngrok tunnel on port {port}...")
        public_url = ngrok.connect(port, "http")
        
        # Format the webhook URL
        webhook_url = f"{public_url}/webhook"
        
        # Print setup instructions
        print("\n=== GitHub Webhook Setup Instructions ===")
        print(f"\n1. Webhook URL to use: {webhook_url}")
        print("\n2. Go to your repository settings:")
        print("   https://github.com/someswarchakraborty/auto_pr_review_agent/settings/hooks")
        print("\n3. Click 'Add webhook' and enter:")
        print("   - Payload URL:", webhook_url)
        print("   - Content type: application/json")
        print("   - Secret: [Your webhook secret from .env file]")
        print("\n4. Under 'Which events would you like to trigger this webhook?':")
        print("   - Select 'Let me select individual events'")
        print("   - Check 'Pull requests' and 'Pull request reviews'")
        print("\n5. Make sure 'Active' is checked")
        print("\n6. Click 'Add webhook'")
        print("\nThe tunnel is now running. Press Ctrl+C to stop.")
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("\nShutting down ngrok tunnel...")
        ngrok.kill()
        
    except Exception as e:
        logger.error(f"Error setting up ngrok tunnel: {str(e)}")
        ngrok.kill()
        raise

if __name__ == "__main__":
    setup_webhook_tunnel()