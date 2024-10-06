import os
import feedparser
from telethon import TelegramClient
import asyncio
from datetime import datetime

# Replace with your actual credentials
API_ID = 12321125            # API ID from my.telegram.org
API_HASH = "6a34b69aa63177ec36f8d9b24c296f40"         # API Hash from my.telegram.org
BOT_USERNAME = "@AutoRenameX_Robot"  # The username of the bot (must start with @)

# RSS feeds URLs
rss_feeds = {
    "Thursday": "https://nyaa.si/?page=rss&q=blue+box+1080p+NF+WEB-DL+DDP5.1+H+264-VARYG&c=1_0&f=0",
    "Sunday": "https://nyaa.si/?page=rss&q=uzumaki+1080p+AMZN+WEB-DL+DDP2.0+H.264+%28Dual-Audio%2C+English-Sub%29&c=1_0&f=0",
    "Saturday": [
        "https://nyaa.si/?page=rss&q=Orb%3A+On+the+Movements+of+the+Earth+varyg&c=1_0&f=0",
        "https://nyaa.si/?page=rss&q=BLEACH%3A+Thousand-Year+Blood+War+-+The+Conflict&c=1_0&f=0"
    ]
}

# Dictionary to store the latest feed ID (or link) for each feed URL
latest_feed = {}

# Function to fetch and parse RSS feed
def fetch_rss_feed(url):
    feed = feedparser.parse(url)
    return feed

# Check if the feed entry is new (not sent before)
def is_new_feed(url, entry_id, sent_feeds):
    global latest_feed

    # If this URL hasn't been checked before, mark the current entry as the latest
    if url not in latest_feed:
        latest_feed[url] = entry_id
        return entry_id not in sent_feeds  # Check against sent feeds

    # If the current entry is newer than the last sent one, update and return True
    if entry_id != latest_feed[url]:
        latest_feed[url] = entry_id
        return entry_id not in sent_feeds  # Check against sent feeds

    # If entry is old, return False
    return False

# Read already sent feeds from the text file
def read_sent_feeds():
    try:
        with open("sent_feed_titles.txt", "r") as log_file:
            sent_feeds = {line.strip() for line in log_file}  # Use a set for faster lookup
            return sent_feeds
    except FileNotFoundError:
        return set()  # Return an empty set if the file does not exist

# Main function to check and send RSS feeds
async def check_and_send_rss(client):
    print("Checking RSS feeds...")  # Debugging line
    sent_feeds = read_sent_feeds()  # Read previously sent feed titles

    for day, feeds in rss_feeds.items():
        if isinstance(feeds, list):
            # Multiple feeds for this day
            for feed_url in feeds:
                feed = fetch_rss_feed(feed_url)
                for entry in feed.entries:
                    # Use entry.link or entry.id as unique identifier for the feed entry
                    entry_id = entry.link

                    if is_new_feed(feed_url, entry_id, sent_feeds):
                        await send_feed_to_telegram(client, entry.title, feed_url)
        else:
            # Single feed
            feed = fetch_rss_feed(feeds)
            for entry in feed.entries:
                entry_id = entry.link

                if is_new_feed(feeds, entry_id, sent_feeds):
                    await send_feed_to_telegram(client, entry.title, feeds)

# Send the feed title and URL in the required format to the bot's private chat
async def send_feed_to_telegram(client, title, feed_url):
    global BOT_USERNAME  # Ensure BOT_USERNAME is treated as a global variable
    message = f"/addtask {feed_url} 0"
    
    try:
        await client.send_message(BOT_USERNAME, message)
    except Exception as e:
        print(f"Error sending message: {e}")

# Schedule to run every hour
async def main():
    # Start the Telethon client using a user session (requires phone number on first login)
    async with TelegramClient('userbot_session', API_ID, API_HASH) as client:
        print("Client started!")
        print("Current Working Directory:", os.getcwd())  # Print current directory
        
        # Check all RSS feeds immediately when the bot starts
        await check_and_send_rss(client)
        
        while True:
            # Wait for 1 hour before checking again (3600 seconds)
            await asyncio.sleep(3600)
            await check_and_send_rss(client)  # Continue checking every hour

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())