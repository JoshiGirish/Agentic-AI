import feedparser
import json
from datetime import datetime, date

# Load feeds from JSON
with open('feeds.json', 'r') as f:
    data = json.load(f)

# Get today's date for comparison
today = date.today()

# Iterate through all feeds
for category, feeds in data['feeds'].items():
    print(f"\n=== {category} ===")
    for feed_url in feeds:
        try:
            d = feedparser.parse(feed_url)
            
            if d.feed:
                # Safely access feed attributes with fallbacks
                title = getattr(d.feed, 'title', 'Unknown')
                link = getattr(d.feed, 'link', 'Unknown')
                
                # Only print if we got meaningful data
                if title and link:
                    print(f"✓ {title} - {link}")
                else:
                    print(f"⚠ Partial data - {feed_url}")
            else:
                print(f"✗ No feed data: {feed_url}")
                
            # Iterate through entries in the feed
            if hasattr(d, 'entries') and d.entries:
                today_entries = []
                for entry in d.entries:
                    # Safely get published date
                    published = getattr(entry, 'published_parsed', None)
                    if published:
                        # Convert to date object
                        try:
                            pub_date = datetime(*published[:6]).date()
                            if pub_date == today:
                                # Safely get entry title
                                entry_title = getattr(entry, 'title', 'Untitled')
                                if entry_title:
                                    today_entries.append(entry_title)
                        except (ValueError, TypeError):
                            pass
                
                # Print today's entries
                if today_entries:
                    print(f"  📅 Published today:")
                    for entry_title in today_entries:
                        print(f"    • {entry_title}")
                
        except Exception as e:
            # Log error but continue processing
            print(f"✗ Error parsing {feed_url}: {str(e)[:50]}")