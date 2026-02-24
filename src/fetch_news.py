import feedparser
from datetime import datetime
import json
import os

# Google News RSS (日本語) で "AI" または "ChatGPT" または "Gemini" または "Claude" を検索
RSS_URLS = [
    "https://news.google.com/rss/search?q=AI+OR+ChatGPT+OR+Gemini+OR+Claude&hl=ja&gl=JP&ceid=JP:ja",
]

def fetch_latest_news():
    """
    RSSフィードから最新のAI関連ニュースを取得する。
    戻り値: [{'title': str, 'link': str, 'published': str}, ...]
    """
    articles = []
    
    for url in RSS_URLS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                # 必要な情報だけを抽出
                article = {
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.published if hasattr(entry, 'published') else datetime.now().isoformat()
                }
                articles.append(article)
        except Exception as e:
            print(f"Error fetching from {url}: {e}")
            
    # 重複排除（念のためリンクベース）
    unique_articles = []
    seen_links = set()
    for article in articles:
        if article['link'] not in seen_links:
            unique_articles.append(article)
            seen_links.add(article['link'])
            
    return unique_articles

if __name__ == "__main__":
    # 単体テスト用
    news = fetch_latest_news()
    print(f"Fetched {len(news)} articles.")
    if news:
        print(json.dumps(news[0], indent=2, ensure_ascii=False))
