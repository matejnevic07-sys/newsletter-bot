import os
import time
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
import httpx
import anthropic

load_dotenv(Path(__file__).parent / ".env")

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_IDS = [
    os.environ["TELEGRAM_CHAT_ID"],
    "289477039",  # Stojan
]

SUBREDDITS = {
    "🔬 Quantum Computing": ["QuantumComputing", "quantum"],
    "🏢 Data Centers": ["datacenters", "sysadmin"],
    "🤖 AI": ["artificial", "MachineLearning", "AINews"],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def fetch_top_posts(subreddit: str, limit: int = 8) -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit}/top.rss?t=day&limit={limit}"
    try:
        time.sleep(1)
        r = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
        r.raise_for_status()

        root = ET.fromstring(r.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)

        posts = []
        for entry in entries[:limit]:
            title_el = entry.find("atom:title", ns)
            link_el = entry.find("atom:link", ns)
            title = title_el.text if title_el is not None else "No title"
            url = link_el.get("href", "") if link_el is not None else ""
            if title and url:
                posts.append({
                    "title": title,
                    "url": url,
                    "subreddit": subreddit,
                })
        print(f"r/{subreddit}: {len(posts)} posts")
        return posts
    except Exception as e:
        print(f"Error fetching r/{subreddit}: {e}")
        return []


def summarize_posts(category: str, posts: list[dict]) -> str:
    if not posts:
        return "Danas nema novih postova."

    posts_text = "\n".join([f"- {p['title']}" for p in posts])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{
            "role": "user",
            "content": f"""Pišeš jutarnji newsletter o temi: {category}

Ovo su današnji top Reddit postovi:
{posts_text}

Izaberi 3 najzanimljivija/najvažnija i napiši summary od 2 rečenice za svaki.
Format tačno ovako:
📌 [originalni naslov posta]
[Summary od 2 rečenice na srpskom — šta je to i zašto je važno]

Preskoči memove i šale. Fokusiraj se na vesti, istraživanja i razvoj.
Piši ISKLJUČIVO na srpskom jeziku."""
        }]
    )
    return response.content[0].text


def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    for chat_id in TELEGRAM_CHAT_IDS:
        httpx.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=15)


def build_and_send():
    today = date.today().strftime("%B %d, %Y")
    header = f"<b>🌅 Jutarnji pregled — {today}</b>\n<i>Tvoj dnevni tech digest</i>"
    send_telegram(header)

    for category, subreddits in SUBREDDITS.items():
        all_posts = []
        for sub in subreddits:
            all_posts.extend(fetch_top_posts(sub))

        top_posts = all_posts[:5]
        summary = summarize_posts(category, top_posts)

        links = "\n".join([
            f'🔗 <a href="{p["url"]}">{p["title"][:70]}</a>'
            for p in top_posts[:3]
        ])

        section = f"\n<b>{category}</b>\n{'─' * 24}\n{summary}\n\n{links}"
        send_telegram(section)

    send_telegram("─" * 24 + "\n<i>Vidimo se sutra! 👋</i>")
    print("Newsletter sent successfully.")


if __name__ == "__main__":
    print("Building morning newsletter...")
    build_and_send()
