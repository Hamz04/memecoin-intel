"""
Seed data: 49 memecoins across ETH, SOL, Base, and BSC with contract addresses.
"""

MEMECOINS = [
    # === ETHEREUM (20) ===
    {"symbol": "PEPE", "name": "Pepe", "chain": "ETH", "contract_address": "0x6982508145454ce325ddbe47a25d4ec3d2311933", "peak_market_cap": 7_000_000_000},
    {"symbol": "SHIB", "name": "Shiba Inu", "chain": "ETH", "contract_address": "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce", "peak_market_cap": 41_000_000_000},
    {"symbol": "FLOKI", "name": "Floki Inu", "chain": "ETH", "contract_address": "0xcf0c122c6b73ff809c693db761e7baebe62b6a2e", "peak_market_cap": 3_200_000_000},
    {"symbol": "MOG", "name": "Mog Coin", "chain": "ETH", "contract_address": "0xaaee1a9723aadb7afa2810263653a34ba2c21c7a", "peak_market_cap": 1_000_000_000},
    {"symbol": "SPX", "name": "SPX6900", "chain": "ETH", "contract_address": "0xe0f63a424a4439cbe457d80e4f4b51ad25b2c56c", "peak_market_cap": 900_000_000},
    {"symbol": "WOJAK", "name": "Wojak", "chain": "ETH", "contract_address": "0x5026f006b85729a8b14553fae6af249ad16c9aab", "peak_market_cap": 200_000_000},
    {"symbol": "TURBO", "name": "Turbo", "chain": "ETH", "contract_address": "0xa35923162c49cf95e6bf26623385eb431ad920d3", "peak_market_cap": 800_000_000},
    {"symbol": "NEIRO", "name": "Neiro", "chain": "ETH", "contract_address": "0x812ba41e071c7b7fa4ebcfb62df5f45f6fa853ee", "peak_market_cap": 1_200_000_000},
    {"symbol": "PEOPLE", "name": "ConstitutionDAO", "chain": "ETH", "contract_address": "0x7a58c0be72be218b41c608b7fe7c5bb630736c71", "peak_market_cap": 1_500_000_000},
    {"symbol": "ELON", "name": "Dogelon Mars", "chain": "ETH", "contract_address": "0x761d38e5ddf6ccf6cf7c55759d5210750b5d60f3", "peak_market_cap": 2_000_000_000},
    {"symbol": "BABYDOGE", "name": "Baby Doge Coin", "chain": "ETH", "contract_address": "0xac57de9c1a09fec648e93eb98875b212db0d460b", "peak_market_cap": 1_800_000_000},
    {"symbol": "SAITAMA", "name": "Saitama", "chain": "ETH", "contract_address": "0xce3f08e664693ca792cbc32acf2003c4ec4d416b", "peak_market_cap": 800_000_000},
    {"symbol": "KISHU", "name": "Kishu Inu", "chain": "ETH", "contract_address": "0xa2b4c0af19cc16a6cfacce81f192b024d625817d", "peak_market_cap": 500_000_000},
    {"symbol": "AKITA", "name": "Akita Inu", "chain": "ETH", "contract_address": "0x3301ee63fb29f863f2333bd4466acb46cd8323e6", "peak_market_cap": 400_000_000},
    {"symbol": "HOGE", "name": "Hoge Finance", "chain": "ETH", "contract_address": "0xfad45e47083e4607302aa43c65fb3106f1cd7607", "peak_market_cap": 300_000_000},
    {"symbol": "LADYS", "name": "Milady Meme Coin", "chain": "ETH", "contract_address": "0x12970e6868f88f6557b76120662c1b3e50a646bf", "peak_market_cap": 250_000_000},
    {"symbol": "MAGA", "name": "MAGA", "chain": "ETH", "contract_address": "0x576e2bed8f7b46d34016198911cdf9886f78bea7", "peak_market_cap": 600_000_000},
    {"symbol": "APU", "name": "Apu Apustaja", "chain": "ETH", "contract_address": "0x594daad7d77592a2b97b725a7ad59d7e188b5bfa", "peak_market_cap": 500_000_000},
    {"symbol": "GROK", "name": "Grok", "chain": "ETH", "contract_address": "0x8390a1da07e376ef7add4be859ba74fb83aa02d5", "peak_market_cap": 400_000_000},
    {"symbol": "GOAT", "name": "Goatseus Maximus", "chain": "ETH", "contract_address": "0x00000000000000000000000000000000deadbeef", "peak_market_cap": 1_300_000_000},

    # === SOLANA (19) ===
    {"symbol": "BONK", "name": "Bonk", "chain": "SOL", "contract_address": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", "peak_market_cap": 3_500_000_000},
    {"symbol": "WIF", "name": "dogwifhat", "chain": "SOL", "contract_address": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm", "peak_market_cap": 4_800_000_000},
    {"symbol": "TRUMP", "name": "Official Trump", "chain": "SOL", "contract_address": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN", "peak_market_cap": 15_000_000_000},
    {"symbol": "PENGU", "name": "Pudgy Penguins", "chain": "SOL", "contract_address": "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv", "peak_market_cap": 5_000_000_000},
    {"symbol": "POPCAT", "name": "Popcat", "chain": "SOL", "contract_address": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", "peak_market_cap": 1_500_000_000},
    {"symbol": "MEW", "name": "cat in a dogs world", "chain": "SOL", "contract_address": "MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5", "peak_market_cap": 1_000_000_000},
    {"symbol": "MYRO", "name": "Myro", "chain": "SOL", "contract_address": "HhJpBhRRn4g56VsyLuT8DL5Bv31HkXqsrahTTUCZeZg4", "peak_market_cap": 300_000_000},
    {"symbol": "SLERF", "name": "Slerf", "chain": "SOL", "contract_address": "7BgBvyjrZX1YKz4oh9mjb8ZScatkkwb8DzFx7LoiVkM3", "peak_market_cap": 700_000_000},
    {"symbol": "BOME", "name": "Book of Meme", "chain": "SOL", "contract_address": "ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82", "peak_market_cap": 1_200_000_000},
    {"symbol": "MELANIA", "name": "Melania Meme", "chain": "SOL", "contract_address": "FUAfBo2jgks6gB4Z4LfZkqSZgzNucisEHqnNebaRxM1P", "peak_market_cap": 2_000_000_000},
    {"symbol": "FARTCOIN", "name": "Fartcoin", "chain": "SOL", "contract_address": "9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump", "peak_market_cap": 2_500_000_000},
    {"symbol": "PNUT", "name": "Peanut the Squirrel", "chain": "SOL", "contract_address": "2qEHjDLDLbuBgRYvsxhc5D6uDWAivNFZGan56P1tpump", "peak_market_cap": 2_200_000_000},
    {"symbol": "MOODENG", "name": "Moo Deng", "chain": "SOL", "contract_address": "ED5nyyWEzpPPiWimP8vYm7sD7TD3LAt3Q3gRTWHzPJBY", "peak_market_cap": 800_000_000},
    {"symbol": "SAMO", "name": "Samoyedcoin", "chain": "SOL", "contract_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU", "peak_market_cap": 200_000_000},
    {"symbol": "PONKE", "name": "Ponke", "chain": "SOL", "contract_address": "5z3EqYQo9HiCEs3R84RCDMu2n7anpDMxRhdK8PSWmrRC", "peak_market_cap": 600_000_000},
    {"symbol": "AI16Z", "name": "ai16z", "chain": "SOL", "contract_address": "HeLp6NuQkmYB4pYWo2zYs22mESHXPQYzXbB8n4V98jwC", "peak_market_cap": 2_400_000_000},
    {"symbol": "ZEREBRO", "name": "Zerebro", "chain": "SOL", "contract_address": "8x5VqbHA8D7NkD52uNuS5nnt3PwA8pLD34ymskeSo2Wn", "peak_market_cap": 800_000_000},
    {"symbol": "GRIFFAIN", "name": "Griffain", "chain": "SOL", "contract_address": "KENJSUYLASHUMfHyy5o4Hp2FdNqZg1AsUPhfH2kYvEP", "peak_market_cap": 500_000_000},
    {"symbol": "RENDER", "name": "Render", "chain": "SOL", "contract_address": "rndrizKT3MK1iimdxRdWabcF7Zg7AR5T4nud4EkHBof", "peak_market_cap": 6_000_000_000},

    # === BASE (6) ===
    {"symbol": "BRETT", "name": "Brett", "chain": "BASE", "contract_address": "0x532f27101965dd16442e59d40670faf5ebb142e4", "peak_market_cap": 2_000_000_000},
    {"symbol": "TOSHI", "name": "Toshi", "chain": "BASE", "contract_address": "0xac1bd2486aaf3b5c0fc3fd868558b082a531b2b4", "peak_market_cap": 400_000_000},
    {"symbol": "DEGEN", "name": "Degen", "chain": "BASE", "contract_address": "0x4ed4e862860bed51a9570b96d89af5e1b0efefed", "peak_market_cap": 1_000_000_000},
    {"symbol": "NORMIE", "name": "Normie", "chain": "BASE", "contract_address": "0x7f12d13b34f5f290bba3b1dd3c7b1e5b1bfe8f60", "peak_market_cap": 200_000_000},
    {"symbol": "TYBG", "name": "Base God", "chain": "BASE", "contract_address": "0x0d97fee56480debf8a4aea8bf2a6aed34c9168c2", "peak_market_cap": 150_000_000},
    {"symbol": "VIRTUAL", "name": "Virtuals Protocol", "chain": "BASE", "contract_address": "0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b", "peak_market_cap": 5_000_000_000},

    # === BSC (4) ===
    {"symbol": "BABYDOGE", "name": "Baby Doge Coin (BSC)", "chain": "BSC", "contract_address": "0xc748673057861a797275CD8A068AbB95A902e8de", "peak_market_cap": 1_800_000_000},
    {"symbol": "SAFEMOON", "name": "SafeMoon V2", "chain": "BSC", "contract_address": "0x42981d0bfbAf196529376EE702F2a9Eb9092fcB5", "peak_market_cap": 6_000_000_000},
    {"symbol": "CAKE", "name": "PancakeSwap", "chain": "BSC", "contract_address": "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82", "peak_market_cap": 11_000_000_000},
    {"symbol": "FLOKI", "name": "Floki (BSC)", "chain": "BSC", "contract_address": "0xfb5b838b6cfeedc2873ab27866079ac55363d37e", "peak_market_cap": 3_200_000_000},
]


def seed_coins(db_session):
    """Insert all memecoins into the database if not already present."""
    from app.models import Coin

    existing = {c.contract_address for c in db_session.query(Coin).all()}
    added = 0
    for coin_data in MEMECOINS:
        if coin_data["contract_address"] not in existing:
            coin = Coin(**coin_data)
            db_session.add(coin)
            added += 1
    db_session.commit()
    return added
