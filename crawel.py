import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import psycopg2
import os

# Supabase / Postgres connection (nastav v environment variables)
DB_URL = os.environ.get("DB_URL")  # např. postgres://user:pass@host:port/dbname

def get_conn():
    return psycopg2.connect(DB_URL)

visited = set()  # již navštívené URL

def crawl(url, max_depth=2, depth=0):
    if url in visited or depth > max_depth:
        return
    visited.add(url)

    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # Titulek
        title = soup.title.string.strip() if soup.title else "Bez názvu"

        # Popisek (meta description)
        desc_tag = soup.find("meta", attrs={"name":"description"})
        description = desc_tag["content"].strip() if desc_tag and "content" in desc_tag.attrs else "Bez popisu"

        # Ikona (favicon)
        icon_tag = soup.find("link", rel=lambda x: x and "icon" in x.lower())
        icon = urljoin(url, icon_tag["href"]) if icon_tag else f"{urlparse(url).scheme}://{urlparse(url).netloc}/favicon.ico"

        # Obsah stránky
        content = soup.get_text()

        # Uložíme stránku do Supabase
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO pages (url, title, description, icon, content)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING
        """, (url, title, description, icon, content))
        conn.commit()
        conn.close()

        print(f"Uloženo: {url} | Titulek: {title} | Popisek: {description[:60]}...")

        # Projdi odkazy na stránce
        for link in soup.find_all("a", href=True):
            href = urljoin(url, link["href"])
            if urlparse(href).scheme in ["http","https"]:
                crawl(href, max_depth, depth+1)

    except Exception as e:
        print(f"Chyba u {url}: {e}")

# Hodně více stránek
urls = [
    "https://google.com",
    "https://youtube.com",
    "https://facebook.com",
    "https://wikipedia.org",
    "https://twitter.com",
    "https://instagram.com",
    "https://linkedin.com",
    "https://reddit.com",
    "https://pinterest.com",
    "https://netflix.com",
    "https://amazon.com",
    "https://apple.com",
    "https://microsoft.com",
    "https://stackoverflow.com",
    "https://github.com",
    "https://medium.com",
    "https://quora.com",
    "https://imdb.com",
    "https://cnn.com",
    "https://bbc.com",
    "https://nytimes.com",
    "https://forbes.com",
    "https://espn.com",
    "https://soundcloud.com",
    "https://spotify.com",
    "https://tumblr.com",
    "https://ebay.com",
    "https://etsy.com",
    "https://walmart.com",
    "https://paypal.com",
    "https://yahoo.com",
    "https://bing.com",
    "https://duckduckgo.com",
    "https://tiktok.com",
    "https://vk.com",
    "https://ok.ru",
    "https://live.com",
    "https://msn.com",
    "https://stackoverflow.blog",
    "https://trello.com",
    "https://slack.com",
    "https://zoom.us",
    "https://dropbox.com",
    "https://hulu.com",
    "https://craigslist.org",
    "https://kickstarter.com",
    "https://buffer.com",
    "https://mailchimp.com",
    "https://etsy.com",
    "https://behance.net",
    "https://dribbble.com",
    "https://vimeo.com",
    "https://flickr.com",
    "https://soundcloud.com",
    "https://spotify.com",
    "https://patreon.com",
    "https://kaggle.com",
    "https://medium.com",
    "https://dev.to",
    "https://hashnode.com",
    "https://news.ycombinator.com",
    "https://producthunt.com",
    "https://reddit.com/r/programming",
    "https://reddit.com/r/technology",
    "https://arxiv.org",
    "https://w3schools.com",
    "https://mdn.com"
]

for url in urls:
    crawl(url, max_depth=1)  # max_depth=1 → jen první stránka + odkazy z ní
