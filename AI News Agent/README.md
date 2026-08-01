# AI News Agent 📰

A Python-based Discord bot that automatically posts RSS feed articles to your Discord server. It fetches articles published yesterday and sends them as rich embed messages with thumbnails.

---

## 🚀 Features

- **Automatic RSS Feed Parsing**: Fetches articles from multiple RSS feeds across different categories
- **Yesterday's Content Only**: Only processes articles published on the previous day
- **Rich Discord Embeds**: Displays article title, link, and category
- **Thumbnail Support**: Extracts and displays article images as Discord thumbnails
- **Categorized Feeds**: Organizes feeds by category (e.g., Technology, Sports, Entertainment)
- **Error Handling**: Gracefully handles feed parsing errors and HTTP failures

---

## 📋 Requirements

- Python 3.8+
- Required packages (install via `requirements.txt`)

```bash
pip install -r requirements.txt
```

---

## 🔧 Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI News Agent
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Discord webhook URL:

```env
WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

> **How to get a Discord Webhook URL:**
> 1. Go to your Discord Server Settings
> 2. Navigate to **Integrations** → **Webhooks**
> 3. Click **New Webhook**
> 4. Give it a name and select a channel
> 5. Click **Copy Webhook URL** and paste it into `.env`

### 3. Configure Feeds

Edit `feeds.json` to add your RSS feeds:

```json
{
  "feeds": {
    "Technology": [
      "https://techcrunch.com/feed/",
      "https://arstechnica.com/feed/"
    ],
    "Sports": [
      "https://espn.com/espn/rss/news"
    ],
    "Entertainment": [
      "https://variety.com/variety-feed/"
    ]
  }
}
```

---

## 📁 Project Structure

```
AI News Agent/
├── .env.example          # Environment variable template
├── .env                  # Your configuration
├── feeds.json            # RSS feed URLs by category
├── feedparse.py          # Main application logic
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## 🛠️ How It Works

1. **Load Configuration**: Reads `.env` for webhook URL and `feeds.json` for RSS feeds
2. **Fetch Feeds**: Parses each RSS feed using the `feedparser` library
3. **Filter by Date**: Only processes articles published on yesterday
4. **Extract Metadata**: Gets title, link, and thumbnail image for each article
5. **Send to Discord**: Posts each article as a rich embed message

---

## 📝 Configuration Files

### `.env.example`

```env
# Discord Webhook URL
# Replace with your actual Discord webhook URL
# Get it from: Discord Server Settings > Integrations > Webhooks
WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

### `feeds.json`

```json
{
  "feeds": {
    "Technology": [
      "https://techcrunch.com/feed/",
      "https://arstechnica.com/feed/"
    ],
    "Sports": [
      "https://espn.com/espn/rss/news"
    ]
  }
}
```

---

## 🚀 Usage

### Run the Bot

```bash
python feedparse.py
```

### Output Example

```
=== Technology ===
  • New AI Model Breaks Records
    Link:  https://techcrunch.com/ai-model
    Image: https://techcrunch.com/wp-content/uploads/ai.jpg
✓ Sent to Discord: New AI Model Breaks Records

=== Sports ===
  • Championship Finals Recap
    Link:  https://espn.com/championship
    Image: None
✓ Sent to Discord: Championship Finals Recap
```

---

## 📦 Dependencies

```
feedparser    # RSS/Atom feed parsing
requests      # HTTP requests for Discord webhook
python-dotenv # Environment variable loading
```
