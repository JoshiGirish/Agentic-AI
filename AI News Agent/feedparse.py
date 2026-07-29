import feedparser
import json
import os
import requests
from datetime import datetime, date, timedelta
from dotenv import load_dotenv


# ============================================================
# Configuration
# ============================================================

load_dotenv()

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL is not set in .env")


# ============================================================
# Helpers
# ============================================================

def get_entry_image(entry):
    """
    Extract an image URL from an RSS/Atom entry.

    Checks common RSS image formats:
      - media:content
      - media:thumbnail
      - enclosure
    """

    # media:content
    media_content = getattr(entry, "media_content", None)
    if media_content:
        for media in media_content:
            media_type = media.get("type", "")
            url = media.get("url")

            if url and (
                media_type.startswith("image/")
                or any(
                    url.lower().split("?")[0].endswith(ext)
                    for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]
                )
            ):
                return url

    # media:thumbnail
    media_thumbnail = getattr(entry, "media_thumbnail", None)
    if media_thumbnail:
        for thumbnail in media_thumbnail:
            url = thumbnail.get("url")
            if url:
                return url

    # enclosure
    enclosures = getattr(entry, "enclosures", None)
    if enclosures:
        for enclosure in enclosures:
            url = enclosure.get("href") or enclosure.get("url")
            media_type = enclosure.get("type", "")

            if url and (
                media_type.startswith("image/")
                or any(
                    url.lower().split("?")[0].endswith(ext)
                    for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]
                )
            ):
                return url

    return None


def get_entry_link(entry):
    """
    Get the destination URL for the feed item.
    """

    link = getattr(entry, "link", None)

    if link:
        return link

    # Fallback: look through entry.links
    for link_data in getattr(entry, "links", []):
        if link_data.get("rel") == "alternate":
            href = link_data.get("href")
            if href:
                return href

    return None


def send_discord_message(title, link=None, image_url=None, category=None):
    """
    Send one feed item to Discord using a webhook embed.
    """

    embed = {
        "title": title,
    }

    # Makes the title clickable
    if link:
        embed["url"] = link

    # Optional category shown below the title
    if category:
        embed["footer"] = {
            "text": category
        }

    # Show feed image as Discord thumbnail
    if image_url:
        embed["thumbnail"] = {
            "url": image_url
        }

    payload = {
        "embeds": [embed]
    }

    response = requests.post(
        WEBHOOK_URL,
        json=payload,
        timeout=15
    )

    response.raise_for_status()

    print(f"✓ Sent to Discord: {title}")


# ============================================================
# Main
# ============================================================

# Load feeds from JSON
with open("feeds.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# Get yesterday's date
yesterday = date.today() - timedelta(days=1)


# Iterate through all feed categories
for category, feeds in data["feeds"].items():

    print(f"\n=== {category} ===")

    for feed_url in feeds:

        try:
            d = feedparser.parse(feed_url)

            if not d.entries:
                print(f"⚠ No entries: {feed_url}")
                continue

            # Iterate through entries
            for entry in d.entries:

                # Safely get published date
                published = getattr(entry, "published_parsed", None)

                if not published:
                    continue

                try:
                    pub_date = datetime(*published[:6]).date()
                except (ValueError, TypeError):
                    continue

                # Only process yesterday's entries
                if pub_date != yesterday:
                    continue

                # Extract title
                entry_title = getattr(entry, "title", "Untitled").strip()

                if not entry_title:
                    entry_title = "Untitled"

                # Extract destination link
                entry_link = get_entry_link(entry)

                # Extract image
                entry_image = get_entry_image(entry)

                print(f"  • {entry_title}")
                print(f"    Link:  {entry_link or 'None'}")
                print(f"    Image: {entry_image or 'None'}")

                # Send one Discord message per item
                send_discord_message(
                    title=entry_title,
                    link=entry_link,
                    image_url=entry_image,
                    category=category
                )

        except requests.HTTPError as e:
            print(f"✗ Discord error: {e}")

        except Exception as e:
            print(f"✗ Error parsing {feed_url}: {str(e)[:100]}")