# CLAUDE.md — Morning Intelligence Newsletter Bot

## Šta je ovaj projekat

Reddit newsletter bot koji svako jutro u 9:00 šalje tech digest na Telegram.
Tri kategorije: Quantum Computing, Data Centers, AI generalno.

## Stack

- **Backend:** Python 3.13 + httpx + Anthropic SDK (claude-sonnet-4-6)
- **Reddit:** RSS feed (`top.rss?t=day`) — bez API ključa, javni endpoint
- **AI:** Claude sumira postove na srpskom
- **Dostava:** Telegram Bot API
- **Scheduler:** GitHub Actions cron (`0 7 * * *` = 9:00 srpsko vreme)
- **Hosting:** Besplatno (GitHub Actions)

## Struktura

```
newsletter-bot/
├── main.py                          # Glavni script
├── requirements.txt
├── .github/workflows/newsletter.yml # GitHub Actions cron job
├── .env                             # API ključevi (nije na GitHub-u)
└── .gitignore
```

## Subredditi po kategorijama

| Kategorija | Subredditi |
|-----------|-----------|
| 🔬 Quantum Computing | r/QuantumComputing, r/quantum |
| 🏢 Data Centers | r/datacenters, r/sysadmin |
| 🤖 AI | r/artificial, r/MachineLearning, r/AINews |

## Kako radi

1. GitHub Actions pokrene `main.py` svako jutro u 9:00
2. Fetchuje top RSS postove iz poslednjih 24h po subredditu
3. Claude izabere top 3 po kategoriji i napiše summary na srpskom
4. Šalje na Telegram sa linkovima

## Telegram

- **Bot:** @morning_matej_bot
- **Primalac 1:** Matej Nevic (chat_id: 5455043190)
- **Primalac 2:** TBD — dodati sutra (treba chat_id od @userinfobot)

## Environment varijable

### Lokalno (`backend/.env`)
```
ANTHROPIC_API_KEY=...
TELEGRAM_TOKEN=8826303565:AAE4ItYUlX6vLR0k1gRY5DZTjDN8pvt-WJg
TELEGRAM_CHAT_ID=5455043190
```

### GitHub Secrets
- `ANTHROPIC_API_KEY`
- `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID`

## TODO

- [ ] Dodati drugog primaoca — čeka se chat_id
- [ ] Rotirati Anthropic API ključeve (oba su bila vidljiva u chatu)

## Lokalno pokretanje

```bat
cd newsletter-bot
python main.py
```

## GitHub Actions

Manuelno pokretanje: GitHub → Actions → Morning Newsletter → Run workflow
