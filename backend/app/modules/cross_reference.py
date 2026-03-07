"""
Cross-Reference Engine: Finds wallets that appear as early buyers across
multiple memecoins. The core of the insider detection system.
"""

import logging
from collections import defaultdict
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Wallet, Trade, Coin, InsiderScore

logger = logging.getLogger(__name__)


class CrossReferenceEngine:
    """Cross-references wallets across multiple memecoins to find recurring insiders."""

    def __init__(self, db: Session):
        self.db = db

    def find_recurring_wallets(self, min_coins: int = 2) -> list:
        """
        Find wallets that bought early in multiple coins.
        Returns list of dicts with wallet info and coins hit.
        """
        results = (
            self.db.query(
                Wallet.id,
                Wallet.address,
                Wallet.chain,
                func.count(func.distinct(Trade.coin_id)).label("coins_hit"),
                func.avg(Trade.minutes_after_launch).label("avg_entry_minutes"),
                func.avg(Trade.roi).label("avg_roi"),
            )
            .join(Trade, Trade.wallet_id == Wallet.id)
            .filter(Trade.trade_type == "BUY")
            .filter(Trade.minutes_after_launch.isnot(None))
            .filter(Trade.minutes_after_launch <= 1440)  # Within 24h
            .group_by(Wallet.id, Wallet.address, Wallet.chain)
            .having(func.count(func.distinct(Trade.coin_id)) >= min_coins)
            .order_by(func.count(func.distinct(Trade.coin_id)).desc())
            .all()
        )

        wallets = []
        for r in results:
            coins = self._get_wallet_coins(r.id)
            wallets.append({
                "wallet_id": r.id,
                "address": r.address,
                "chain": r.chain,
                "coins_hit": r.coins_hit,
                "avg_entry_minutes": round(r.avg_entry_minutes, 1) if r.avg_entry_minutes else None,
                "avg_roi": round(r.avg_roi, 2) if r.avg_roi else None,
                "coins": coins,
            })

        return wallets

    def _get_wallet_coins(self, wallet_id: int) -> list:
        """Get list of coins a wallet has traded."""
        trades = (
            self.db.query(Trade, Coin)
            .join(Coin, Trade.coin_id == Coin.id)
            .filter(Trade.wallet_id == wallet_id)
            .filter(Trade.trade_type == "BUY")
            .order_by(Trade.traded_at.asc())
            .all()
        )
        return [
            {
                "symbol": coin.symbol,
                "chain": coin.chain,
                "minutes_after_launch": round(trade.minutes_after_launch, 1) if trade.minutes_after_launch else None,
                "roi": round(trade.roi, 2) if trade.roi else None,
                "amount_usd": trade.amount_usd,
            }
            for trade, coin in trades
        ]

    def get_overlap_map(self, min_score: int = 50) -> dict:
        """
        Build an overlap map showing which insiders overlap across coins.
        Returns {coin_symbol: [wallet_addresses]} for visualization.
        """
        scored_wallets = (
            self.db.query(InsiderScore)
            .filter(InsiderScore.score >= min_score)
            .all()
        )

        overlap = defaultdict(list)
        for score_record in scored_wallets:
            coins = score_record.coins_list or []
            wallet_addr = score_record.wallet.address if score_record.wallet else "unknown"
            for coin_symbol in coins:
                overlap[coin_symbol].append({
                    "address": wallet_addr,
                    "score": score_record.score,
                    "tier": score_record.tier,
                })

        return dict(overlap)

    def find_wallet_connections(self, wallet_address: str) -> dict:
        """
        Find other wallets that frequently appear alongside a given wallet.
        Useful for detecting wallet clusters (same entity, multiple addresses).
        """
        wallet = self.db.query(Wallet).filter(Wallet.address == wallet_address).first()
        if not wallet:
            return {"error": "Wallet not found"}

        # Get coins this wallet traded
        wallet_coins = (
            self.db.query(Trade.coin_id)
            .filter(Trade.wallet_id == wallet.id)
            .filter(Trade.trade_type == "BUY")
            .distinct()
            .all()
        )
        coin_ids = [c[0] for c in wallet_coins]

        if not coin_ids:
            return {"wallet": wallet_address, "connections": []}

        # Find other wallets that traded the same coins
        co_traders = (
            self.db.query(
                Wallet.address,
                func.count(func.distinct(Trade.coin_id)).label("shared_coins"),
            )
            .join(Trade, Trade.wallet_id == Wallet.id)
            .filter(Trade.coin_id.in_(coin_ids))
            .filter(Trade.trade_type == "BUY")
            .filter(Wallet.id != wallet.id)
            .group_by(Wallet.address)
            .having(func.count(func.distinct(Trade.coin_id)) >= 2)
            .order_by(func.count(func.distinct(Trade.coin_id)).desc())
            .limit(20)
            .all()
        )

        return {
            "wallet": wallet_address,
            "total_coins": len(coin_ids),
            "connections": [
                {"address": addr, "shared_coins": count}
                for addr, count in co_traders
            ],
        }
