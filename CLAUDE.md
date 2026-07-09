# CLAUDE.md — Morning Intelligence Newsletter Bot

## Šta je ovaj projekat

Reddit newsletter bot koji svako jutro u 9:00 šalje tech digest na Telegram.
Dve kategorije: Quantum Computing i AI (fokus: novi modeli, alati, cene API-ja/pretplata, benchmarci, open-source izdanja).
Dva primaoca: Matej i Stojan.

**Pravilo: nikad prazan newsletter.** Prompt uvek bira top 3 vesti i u sporom danu; ako Reddit RSS potpuno padne, baca grešku (stiže error notifikacija) umesto praznog digesta.

## Stack

- **Backend:** Python 3.13 + httpx + Anthropic SDK (claude-sonnet-4-6)
- **Reddit:** RSS feed (`top.rss?t=day`) — bez API ključa, javni endpoint
- **AI:** Dvostepeni Claude agent — interno bira top 3, zatim piše investment analizu na srpskom
- **Dostava:** Telegram Bot API
- **Scheduler:** GitHub Actions cron (`0 7 * * *` = 9:00 srpsko vreme)
- **Hosting:** Besplatno (GitHub Actions)

## Struktura

```
newsletter-bot/
├── main.py                           # Glavni script
├── requirements.txt                  # Pinned: anthropic==0.40.0, httpx==0.27.0
├── .github/
│   └── workflows/
│       ├── newsletter.yml            # Cron job — 9:00 svako jutro
│       └── keepalive.yml             # Mesečni commit da GitHub ne ugasi cron
├── keepalive.txt                     # Auto-generisan od keepalive workflow-a
├── .env                              # API ključevi (nije na GitHub-u)
└── .gitignore
```

## Subredditi po kategorijama

| Kategorija | Subredditi |
|-----------|-----------|
| 🔬 Quantum Computing | r/QuantumComputing, r/quantum, r/QuantumInformation |
| 🤖 AI | r/artificial, r/MachineLearning, r/AINews, r/OpenAI, r/ClaudeAI, r/ChatGPT, r/LocalLLaMA, r/singularity |

Data Centers kategorija izbačena 2026-07-09 — fokus samo na quantum + AI.

## Kako radi — dvostepeni agent

1. GitHub Actions pokrene `main.py` svako jutro u 9:00
2. Fetchuje top RSS postove iz poslednjih 24h po subredditu (Chrome User-Agent, 1s sleep između requesta)
3. **Korak 1 (interno):** Claude primi numerisanu listu svih postova → odabere 3 najzanimljivija (prioritet: novi modeli, alati, cene, benchmarci, open-source) i ignoriše meme/humor (odgovara samo brojevima: `2, 7, 4`)
4. **Korak 2 (output):** Claude dobije sve postove + odabrana 3 → piše digest na ekavici: šta se desilo, zašto je zanimljivo, konkretna imena modela/alata i cene. UVEK šalje 3 vesti, nikad "nema vesti"
5. Šalje na Telegram sa linkovima, sve na srpskom

**Zašto dvostepeni:** Korisnik ne želi da vidi "So what?" labele — Claude treba da sam preispita vesti i dostavi samo finalni zaključak.

## Telegram

- **Bot:** @morning_matej_bot
- **Primalac 1:** Matej Nevic (chat_id: 5455043190)
- **Primalac 2:** Stojan (chat_id: 289477039)

## Sigurnost i pouzdanost

- **Keepalive:** `keepalive.yml` commituje `keepalive.txt` svakog 1. u mesecu → GitHub ne gasi cron zbog neaktivnosti (60-day policy)
- **Error notifikacija:** Ako `build_and_send()` padne, Telegram poruka sa greškom se šalje odmah
- **Truncation:** Telegram poruke >4000 karaktera se automatski seku
- **Pinned verzije:** `requirements.txt` koristi fiksne verzije — ne može se slomiti zbog update-a
- **RSS umesto API:** Bez autentifikacije, ne blokira se sa GitHub Actions IP-ova

## Environment varijable

### Lokalno (`.env`)
```
ANTHROPIC_API_KEY=...
TELEGRAM_TOKEN=...
TELEGRAM_CHAT_ID=5455043190
```

### GitHub Secrets (Settings → Secrets → Actions)
- `ANTHROPIC_API_KEY`
- `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID`

## Jedino što zahteva pažnju

- **Anthropic krediti** — pratiti na console.anthropic.com (~6 API poziva/dan)

## Lokalno pokretanje

```bat
cd newsletter-bot
python main.py
```

## GitHub Actions

Manuelno pokretanje: GitHub → Actions → Morning Newsletter → Run workflow
