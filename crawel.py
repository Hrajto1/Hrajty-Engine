import requests
from bs4 import BeautifulSoup
import sqlite3
from urllib.parse import urljoin, urlparse

# Připojení k databázi
conn = sqlite3.connect('hrajty.db')
c = conn.cursor()

# Vytvoření tabulky (rozšířená o description + icon)
c.execute('''
CREATE TABLE IF NOT EXISTS pages (
    url TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    icon TEXT,
    content TEXT
)
''')
conn.commit()

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
        desc_tag = soup.find("meta", attrs={"name": "description"})
        description = desc_tag["content"].strip() if desc_tag and "content" in desc_tag.attrs else "Bez popisu"

        # Ikona (favicon)
        icon_tag = soup.find("link", rel=lambda x: x and "icon" in x.lower())
        if icon_tag and "href" in icon_tag.attrs:
            icon = urljoin(url, icon_tag["href"])
        else:
            parsed = urlparse(url)
            icon = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"

        # Text obsahu
        text = soup.get_text()

        # Uložíme stránku do DB
        c.execute(
            "INSERT OR IGNORE INTO pages (url, title, description, icon, content) VALUES (?, ?, ?, ?, ?)",
            (url, title, description, icon, text)
        )
        conn.commit()
        print(f"Uloženo: {url} | Titulek: {title} | Popisek: {description[:60]}...")

        # Projde všechny odkazy na stránce
        for link in soup.find_all("a", href=True):
            href = urljoin(url, link["href"])
            if urlparse(href).scheme in ["http", "https"]:
                crawl(href, max_depth, depth + 1)

    except Exception as e:
        print(f"Chyba u {url}: {e}")

# Seznam stránek k prohledání
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
    "https://medium.com",
    "https://hulu.com",
    "https://craigslist.org",
    "https://kickstarter.com",
    "https://buffer.com",
    "https://mailchimp.com"
]

for url in urls:
    crawl(url, max_depth=1)  # max_depth=1 → jen první stránku + odkazy z ní

conn.close()
