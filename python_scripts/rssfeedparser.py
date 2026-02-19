import feedparser
import json

# URL of the RSS feed
rss_url = 'https://www.globalenergyworld.com/rss-feed/?channelId=27'

# Parse the RSS feed
feed = feedparser.parse(rss_url)

# Prepare a list to hold the extracted feed data
feed_data = []

# Extract relevant information from each entry in the feed
for entry in feed.entries:
    feed_entry = {
        "title": entry.title,
        "link": entry.link,
        "published": entry.published,
        "summary": entry.summary
    }
    feed_data.append(feed_entry)

# Convert the feed data to JSON format
feed_json = json.dumps(feed_data, indent=4)

# Output the JSON data
print(feed_json)
