"""
FastMCP Server for Discord Posting functionality.

This server exposes a tool to post news articles to Discord using webhooks.
"""

import os
import logging
from typing import Optional
import fastmcp
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Initialize FastMCP server
mcp = fastmcp.FastMCP("Discord Poster", "Post news articles to Discord")


def get_webhook_url() -> Optional[str]:
    """Get the Discord webhook URL from environment variable."""
    return os.getenv("DISCORD_WEBHOOK_URL")


def get_discord_config() -> dict:
    """Get current Discord configuration."""
    return {
        "webhook_url_configured": bool(get_webhook_url()),
        "webhook_url": get_webhook_url()
    }


@mcp.tool()
def post_discord_article(
    title: str,
    content: str,
    url: str,
    image_url: Optional[str] = None,
    category: Optional[str] = None,
    webhook_url: Optional[str] = None
) -> dict:
    """
    Post a news article to Discord.
    
    This tool sends a formatted message to a Discord channel using a webhook.
    The message includes the article title, content, and optionally a thumbnail image.
    
    Args:
        title: The title of the news article.
        content: The summary or content of the article.
        url: The URL of the original article.
        image_url: Optional URL of a thumbnail image for the post.
        category: Optional category or section of the article (shown as footer).
        webhook_url: Optional webhook URL. If not provided, uses DISCORD_WEBHOOK_URL env var.
    
    Returns:
        A dictionary with the posting result:
        - success: bool indicating if the post was successful
        - message: Description of the result
        - post_id: The webhook response ID (if applicable)
        - error: Error message if posting failed
    
    Example:
        >>> post_discord_article(
        ...     title="New AI Model Released",
        ...     content="A groundbreaking new AI model has been released...",
        ...     url="https://example.com/article",
        ...     image_url="https://example.com/image.jpg",
        ...     category="Technology"
        ... )
        {'success': True, 'message': 'Posted to Discord', 'post_id': 'webhook_response_id'}
    """
    # Use provided webhook URL or fall back to environment variable
    effective_webhook_url = webhook_url or get_webhook_url()
    
    if not effective_webhook_url:
        return {
            "success": False,
            "message": "No webhook URL configured. Set DISCORD_WEBHOOK_URL environment variable.",
            "error": "No webhook URL configured"
        }
    
    # Prepare the embed data
    embed_data = {
        "title": title,
        "url": url,
        "color": 5763719,  # Discord blue color
    }
    
    # Add description (content)
    # Truncate content if too long
    if len(content) > 4000:
        content = content[:4000] + "..."
    embed_data["description"] = content
    
    # Add thumbnail image if provided
    if image_url:
        embed_data["thumbnail"] = {"url": image_url}
    
    # Add footer with category if provided
    if category:
        embed_data["footer"] = {"text": category}
    
    # Add timestamp
    import datetime
    embed_data["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    
    try:
        
        # Send the webhook payload
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AI-News-Agent-Discord-Poster/1.0"
        }
        
        response = requests.post(
            effective_webhook_url,
            json={"embeds": [embed_data]},
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 204:
            return {
                "success": True,
                "message": f"Posted to Discord: {title}",
                "post_id": "webhook_post"
            }
        elif response.status_code == 401:
            return {
                "success": False,
                "message": "Invalid webhook URL. Please check your configuration.",
                "error": "Invalid webhook URL (401 Unauthorized)"
            }
        elif response.status_code == 429:
            return {
                "success": False,
                "message": "Rate limit exceeded. Please wait before trying again.",
                "error": "Rate limit exceeded (429 Too Many Requests)"
            }
        else:
            error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            return {
                "success": False,
                "message": f"Failed to post to Discord",
                "error": error_msg
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "Request timed out",
            "error": "Connection timed out (timeout)"
        }
    except requests.exceptions.ConnectionError as e:
        return {
            "success": False,
            "message": "Could not connect to Discord",
            "error": f"Connection error: {str(e)[:100]}"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": "An error occurred while posting",
            "error": f"Request error: {str(e)[:100]}"
        }
    except Exception as e:
        logger.error(f"Unexpected error in post_discord_article: {e}")
        return {
            "success": False,
            "message": "An unexpected error occurred",
            "error": str(e)[:200]
        }


@mcp.tool()
def configure_discord(webhook_url: Optional[str] = None) -> dict:
    """
    Configure the Discord webhook URL.
    
    Note: This tool doesn't persist the webhook URL. The URL should be set
    via the DISCORD_WEBHOOK_URL environment variable for persistence across
    container restarts.
    
    Args:
        webhook_url: The Discord webhook URL to use. If not provided,
                     reads from DISCORD_WEBHOOK_URL environment variable.
    
    Returns:
        A dictionary with the configuration status.
    """
    if webhook_url:
        logger.info(f"Discord webhook URL configured (length: {len(webhook_url)})")
        return {
            "success": True,
            "message": "Webhook URL configured",
            "webhook_url": webhook_url if webhook_url.startswith("https://discord.com/api/webhooks") else "Webhook URL configured"
        }
    else:
        current_url = get_webhook_url()
        if current_url:
            return {
                "success": True,
                "message": "Webhook URL already configured",
                "webhook_url": current_url if current_url.startswith("https://discord.com/api/webhooks") else "Webhook URL configured"
            }
        else:
            return {
                "success": False,
                "message": "No webhook URL configured",
                "error": "Set DISCORD_WEBHOOK_URL environment variable"
            }


@mcp.tool()
def get_discord_status() -> dict:
    """
    Get the current status of the Discord integration.
    
    Returns:
        A dictionary with the current configuration status.
    """
    config = get_discord_config()
    return {
        "status": "ready" if config["webhook_url_configured"] else "not_configured",
        **config
    }


if __name__ == "__main__":
    # Run the server for local testing
    import uvicorn
    uvicorn.run(__name__, host="0.0.0.0", port=8000)