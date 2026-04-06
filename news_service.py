import requests
from bs4 import BeautifulSoup
import time
import feedparser # Need to install: pip install feedparser

class NewsService:
    def __init__(self, rss_feeds=None):
        self.rss_feeds = rss_feeds or [
            "https://habr.com/ru/rss/articles/", # Habr Technology
            "https://www.ixbt.com/export/news.rss" # iXBT Tech News
        ]
        self.seen_guids = set()

    def fetch_latest_news(self):
        latest_news = []
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    if entry.link not in self.seen_guids:
                        news_item = {
                            "title": entry.title,
                            "summary": entry.get('summary', entry.get('description', '')),
                            "link": entry.link,
                            "published": entry.get('published', '')
                        }
                        latest_news.append(news_item)
                        # self.seen_guids.add(entry.link) # Only add to seen AFTER processing
            except Exception as e:
                print(f"Error fetching {feed_url}: {e}")
        return latest_news

    def summarize_news(self, news_item):
        # In a real app, use an LLM API here
        # For now, just return a formatted version
        summary = f"🔥 {news_item['title']}\n\n"
        # Removing HTML tags from summary if any
        clean_summary = BeautifulSoup(news_item['summary'], "html.parser").get_text()
        summary += f"{clean_summary[:200]}...\n\n"
        summary += f"Читать далее: {news_item['link']}"
        return summary

if __name__ == "__main__":
    service = NewsService()
    news = service.fetch_latest_news()
    if news:
        print(f"Found {len(news)} new items.")
        print(service.summarize_news(news[0]))
    else:
        print("No new news found.")
