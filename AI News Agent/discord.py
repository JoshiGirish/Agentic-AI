import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read WEBHOOK_URL from environment variables with a default value
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

def send_discord_message(message):
    response = requests.post(
        WEBHOOK_URL,
        json={"content": message}
    )

    response.raise_for_status()
    print("Message sent!")


send_discord_message("Your daily dose of AI! 🚀")