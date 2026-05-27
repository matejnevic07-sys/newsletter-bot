import os
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
import httpx
import anthropic

load_dotenv(Path(__file__).parent / ".env")

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SUBREDDITS = {
    "🔬 Quantum Computing": ["QuantumComputing", "quantum"],
    "🏢 Data Centers": ["datacenters", "sysadmin"],
    "🤖 AI": ["artificial", "MachineLearning", "AINews"],
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def fetch_top_posts(subreddit: str, limit: int = 8) -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit}/top.json?t=day&limit={limit}"
    try:
        r = httpx.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        posts = r.json()["data"]["children"]
        return [
            {
                "title": p["data"]["title"],
                "score": p["data"]["score"],
                "comments": p["data"]["num_comments"],
                "url": f"https://reddit.com{p['data']['permalink']}",
                "subreddit": subreddit,
            }
            for p in posts
            if not p["data"].get("stickied")
        ]
    except Exception as e:
        print(f"Error fetching r/{subreddit}: {e}")
        return []


def summarize_posts(category: str, posts: list[dict]) -> str:
    if not posts:
        return "No posts found today."

    posts_text = "\n".join([
        f"- {p['title']} (👍 {p['score']} upvotes, 💬 {p['comments']} comments)"
        for p in posts
    ])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{
            "role": "user",
            "content": f"""You are writing a morning newsletter section about: {category}

Here are today's top Reddit posts:
{posts_text}

Izaberi 3 najzanimljivija/najvažnija posta i napiši summary od 2 rečenice za svaki.
Format tačno ovako za svaki post:
📌 [originalni naslov posta]
[Tvoj summary od 2 rečenice koji objašnjava šta je to i zašto je važno]

Preskoči memove, šale i postove lošeg kvaliteta. Fokusiraj se na stvarne vesti, istraživanja i razvoj.
Piši ISKLJUČIVO na srpskom jeziku."""
        }]
    )
    return response.content[0].text


def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    httpx.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
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

        all_posts.sort(key=lambda x: x["score"], reverse=True)
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
