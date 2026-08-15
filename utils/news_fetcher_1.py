import feedparser
import requests
from bs4 import BeautifulSoup

def fetch_rss(limit_per_feed=5):
    articles = []
    from config import RSS_FEEDS
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:limit_per_feed]:
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.get("summary", "")[:500],
                    "published": entry.get("published", "")
                })
        except Exception as e:
            print(f"RSS fail {url}: {e}")
    return articles

def fetch_article_text(url):
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs[:10]])
        return text[:2000]
    except:
        return ""
