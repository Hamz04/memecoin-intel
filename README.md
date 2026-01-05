# Memecoin Insider Intelligence Platform

Track recurring insider wallets across every memecoin that hit $100M+ market cap. Find the wallets that keep showing up early — across PEPE, BONK, WIF, TRUMP, BRETT, and 44 more mega-runners.

## What It Does

1. **Scans** 49+ memecoins across Ethereum, Solana, Base, and BSC
2. **Cross-references** early buyers to find wallets that hit multiple mega-runners
3. **Scores** wallets 0-100 based on coins hit, win rate, entry speed, and ROI
4. **Alerts** when tracked insiders buy something new (Telegram for Elite)
5. **Monetizes** via Stripe subscriptions: Free / Pro ($49/mo) / Elite ($199/mo)

## Architecture

```
backend/          FastAPI + Python forensic engine
  app/
    modules/
      chain_scanner.py      Dune Analytics + Etherscan/Solscan APIs
      cross_reference.py    Find wallets across multiple coins
      insider_scorer.py     Score wallets 0-100 with behavioral flags
      alert_system.py       Real-time monitoring + notifications
      subscription.py       Stripe payments + tier management
    routes/
      insiders.py           Leaderboard, wallet detail, overlap map
      coins.py              Coin list, forensic analysis
      alerts.py             Alert feed, subscription, stats
    models.py               SQLAlchemy models (6 tables)
    seed_data.py            49 memecoins with contract addresses
    telegram_bot.py         Telegram bot for Elite alerts
    main.py                 FastAPI app entry point

frontend/         React + Tailwind dark-themed dashboard
  src/
    pages/
      Dashboard.jsx         Stats overview + top insiders preview
      Leaderboard.jsx       Full insider wallet rankings
      CoinForensics.jsx     Per-coin early buyer analysis
      WalletDetail.jsx      Deep dive into any wallet
      Alerts.jsx            Live alerts feed (auto-refresh)
      Pricing.jsx           Landing page + Stripe checkout
    components/
      Layout.jsx            Sidebar navigation + tier indicator
```

## Quick Start

### With Docker (recommended)
```bash
cp backend/.env.example backend/.env
# Fill in your API keys in backend/.env
docker-compose up --build
```
- Frontend: http://localhost:3000
- API: http://localhost:8000/docs

### Manual Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Fill in API keys
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## API Keys Required

| Service | Free Tier | Purpose | Get Key |
|---------|-----------|---------|---------|
| **Dune Analytics** | 2,500 queries/mo | Historical on-chain data | [dune.com/settings/api](https://dune.com/settings/api) |
| **Etherscan** | 5 calls/sec | Ethereum token transfers | [etherscan.io/myapikey](https://etherscan.io/myapikey) |
| **Solscan** | Free tier | Solana token data | [pro-api.solscan.io](https://pro-api.solscan.io) |
| **Basescan** | 5 calls/sec | Base chain data | [basescan.org/myapikey](https://basescan.org/myapikey) |
| **Bscscan** | 5 calls/sec | BSC chain data | [bscscan.com/myapikey](https://bscscan.com/myapikey) |
| **Stripe** | Pay-as-you-go | Subscriptions | [dashboard.stripe.com](https://dashboard.stripe.com/apikeys) |
| **Telegram** | Free | Bot alerts | [t.me/BotFather](https://t.me/BotFather) |

## Subscription Tiers

| Feature | Free | Pro ($49/mo) | Elite ($199/mo) |
|---------|------|-------------|-----------------|
| Insider wallets shown | 5 | Unlimited | Unlimited |
| Min insider score | 85+ | 50+ | 30+ |
| Early buyers per coin | 10 | 100 | 500 |
| Overlap map | No | Yes | Yes |
| Alerts feed | Limited | Full | Full |
| Telegram alerts | No | No | Real-time |
| Behavioral flags | No | No | Yes |
| API access | No | No | Yes |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/insiders/leaderboard` | Insider wallet rankings |
| GET | `/api/insiders/wallet/{address}` | Wallet deep dive |
| GET | `/api/insiders/overlap-map` | Cross-reference visualization |
| GET | `/api/coins` | List tracked memecoins |
| GET | `/api/coins/{symbol}/forensics` | Coin forensic analysis |
| GET | `/api/alerts/feed` | Live alerts feed |
| POST | `/api/subscribe/checkout` | Create Stripe checkout |
| POST | `/api/subscribe/webhook` | Stripe webhook handler |
| GET | `/api/scan/trigger` | Manually trigger chain scan |

## How the Scoring Works

Insider Score (0-100) is a weighted composite:
- **Coins Hit (30%)** — More $100M+ coins caught early = higher score
- **Win Rate (25%)** — Percentage of profitable trades
- **Entry Speed (20%)** — How fast after launch they buy (minutes)
- **ROI Magnitude (15%)** — Average return multiplier
- **Market Cap Impact (10%)** — Catching bigger coins = more weight

Tiers: LEGENDARY (85+) | ELITE (70+) | NOTABLE (50+) | WATCHLIST (30+) | NOISE (<30)

## Coins Tracked (49)

Ethereum (20): PEPE, SHIB, FLOKI, MOG, SPX, WOJAK, TURBO, NEIRO, PEOPLE, ELON, BABYDOGE, SAITAMA, KISHU, AKITA, HOGE, LADYS, MAGA, APU, GROK, GOAT

Solana (19): BONK, WIF, TRUMP, PENGU, POPCAT, MEW, MYRO, SLERF, BOME, MELANIA, FARTCOIN, PNUT, MOODENG, SAMO, PONKE, AI16Z, ZEREBRO, GRIFFAIN, RENDER

Base (6): BRETT, TOSHI, DEGEN, NORMIE, TYBG, VIRTUAL

BSC (4): BABYDOGE, SAFEMOON, CAKE, FLOKI

## License
MIT
