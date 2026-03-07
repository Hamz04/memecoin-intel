"""
Insider Scorer: Computes a composite 0-100 score for each wallet based on
coins hit, win rate, entry speed, ROI magnitude, and market cap impact.
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Wallet, Trade, Coin, InsiderScore

logger = logging.getLogger(__name__)

# Score weights
WEIGHTS = {
    "coins_hit": 0.30,
    "win_rate": 0.25,
    "entry_speed": 0.20,
    "roi_magnitude": 0.15,
    "mcap_impact": 0.10,
}

# Tier thresholds
TIERS = [
    (85, "LEGENDARY"),
    (70, "ELITE"),
    (50, "NOTABLE"),
    (30, "WATCHLIST"),
    (0, "NOISE"),
]

# Behavioral flags
FLAG_DEFINITIONS = {
    "SNIPER": "Consistently buys within 10 minutes of launch",
    "DIAMOND_HANDS": "Holds positions for 30+ days on average",
    "MULTI_CHAIN": "Active across 2+ blockchains",
    "CLUSTER_MEMBER": "Trades in sync with other flagged wallets",
    "WHALE": "Average position size > $50,000",
    "PERFECT_TIMING": "Win rate above 90%",
    "SERIAL_HITTER": "Hit 5+ mega-runners early",
}


class InsiderScorer:
    """Computes insider scores for wallets based on trading behavior."""

    def __init__(self, db: Session):
        self.db = db

    def score_wallet(self, wallet_id: int) -> Optional[dict]:
        """Compute and store the insider score for a single wallet."""
        wallet = self.db.query(Wallet).get(wallet_id)
        if not wallet:
            return None

        trades = (
            self.db.query(Trade, Coin)
            .join(Coin, Trade.coin_id == Coin.id)
            .filter(Trade.wallet_id == wallet_id)
            .filter(Trade.trade_type == "BUY")
            .all()
        )

        if not trades:
            return None

        # Calculate component scores
        coins_hit = self._score_coins_hit(trades)
        win_rate = self._score_win_rate(trades)
        entry_speed = self._score_entry_speed(trades)
        roi_mag = self._score_roi_magnitude(trades)
        mcap_impact = self._score_mcap_impact(trades)

        # Weighted composite
        composite = (
            coins_hit * WEIGHTS["coins_hit"]
            + win_rate * WEIGHTS["win_rate"]
            + entry_speed * WEIGHTS["entry_speed"]
            + roi_mag * WEIGHTS["roi_magnitude"]
            + mcap_impact * WEIGHTS["mcap_impact"]
        )

        composite = min(100, max(0, composite))
        tier = self._get_tier(composite)
        flags = self._detect_flags(wallet, trades, composite)
        coins_list = list({coin.symbol for trade, coin in trades})

        # Upsert InsiderScore
        score_record = (
            self.db.query(InsiderScore)
            .filter(InsiderScore.wallet_id == wallet_id)
            .first()
        )

        if score_record:
            score_record.score = composite
            score_record.tier = tier
            score_record.coins_hit_score = coins_hit
            score_record.win_rate_score = win_rate
            score_record.entry_speed_score = entry_speed
            score_record.roi_score = roi_mag
            score_record.mcap_impact_score = mcap_impact
            score_record.behavioral_flags = flags
            score_record.coins_list = coins_list
            score_record.last_computed = datetime.utcnow()
        else:
            score_record = InsiderScore(
                wallet_id=wallet_id,
                score=composite,
                tier=tier,
                coins_hit_score=coins_hit,
                win_rate_score=win_rate,
                entry_speed_score=entry_speed,
                roi_score=roi_mag,
                mcap_impact_score=mcap_impact,
                behavioral_flags=flags,
                coins_list=coins_list,
            )
            self.db.add(score_record)

        # Update wallet aggregates
        wallet.total_coins_hit = len(coins_list)
        wallet.total_trades = len(trades)
        wallet.avg_entry_time_minutes = self._avg_entry_time(trades)
        wallet.avg_roi = self._avg_roi(trades)
        wallet.win_rate = self._raw_win_rate(trades)

        self.db.commit()

        return score_record.to_dict()

    def score_all_wallets(self) -> list:
        """Recompute scores for all wallets with trades."""
        wallet_ids = (
            self.db.query(Trade.wallet_id)
            .filter(Trade.trade_type == "BUY")
            .distinct()
            .all()
        )

        results = []
        for (wid,) in wallet_ids:
            result = self.score_wallet(wid)
            if result:
                results.append(result)
                logger.info(f"Scored wallet {result['wallet_address']}: {result['score']} ({result['tier']})")

        logger.info(f"Scored {len(results)} wallets total")
        return results

    # ------------------------------------------------------------------
    # Component scorers (each returns 0-100)
    # ------------------------------------------------------------------
    def _score_coins_hit(self, trades: list) -> float:
        """More unique coins = higher score. Max at 10+ coins."""
        unique_coins = len({coin.id for trade, coin in trades})
        return min(100, (unique_coins / 10) * 100)

    def _score_win_rate(self, trades: list) -> float:
        """Percentage of trades with positive ROI."""
        rois = [t.roi for t, c in trades if t.roi is not None]
        if not rois:
            return 50  # neutral
        wins = sum(1 for r in rois if r > 0)
        return (wins / len(rois)) * 100

    def _score_entry_speed(self, trades: list) -> float:
        """Faster entry = higher score. Score decays as minutes increase."""
        times = [t.minutes_after_launch for t, c in trades if t.minutes_after_launch is not None]
        if not times:
            return 0
        avg_minutes = sum(times) / len(times)
        # 0 min = 100, 60 min = 50, 1440 min (24h) = 0
        score = max(0, 100 - (avg_minutes / 14.4))
        return min(100, score)

    def _score_roi_magnitude(self, trades: list) -> float:
        """Higher average ROI = higher score. Capped at 100x."""
        rois = [t.roi for t, c in trades if t.roi is not None and t.roi > 0]
        if not rois:
            return 0
        avg_roi = sum(rois) / len(rois)
        return min(100, (avg_roi / 100) * 100)

    def _score_mcap_impact(self, trades: list) -> float:
        """Catching bigger coins (higher peak mcap) = more weight."""
        mcaps = [c.peak_market_cap for t, c in trades if c.peak_market_cap]
        if not mcaps:
            return 0
        avg_mcap = sum(mcaps) / len(mcaps)
        # $100M = 20, $1B = 50, $10B+ = 100
        score = min(100, (avg_mcap / 10_000_000_000) * 100)
        return score

    # ------------------------------------------------------------------
    # Behavioral flags
    # ------------------------------------------------------------------
    def _detect_flags(self, wallet, trades: list, score: float) -> list:
        flags = []

        times = [t.minutes_after_launch for t, c in trades if t.minutes_after_launch is not None]
        if times and (sum(times) / len(times)) < 10:
            flags.append("SNIPER")

        rois = [t.roi for t, c in trades if t.roi is not None]
        if rois and len(rois) >= 3:
            wr = sum(1 for r in rois if r > 0) / len(rois)
            if wr > 0.9:
                flags.append("PERFECT_TIMING")

        chains = {c.chain for t, c in trades}
        if len(chains) >= 2:
            flags.append("MULTI_CHAIN")

        amounts = [t.amount_usd for t, c in trades if t.amount_usd]
        if amounts and (sum(amounts) / len(amounts)) > 50000:
            flags.append("WHALE")

        unique_coins = len({c.id for t, c in trades})
        if unique_coins >= 5:
            flags.append("SERIAL_HITTER")

        return flags

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_tier(self, score: float) -> str:
        for threshold, tier_name in TIERS:
            if score >= threshold:
                return tier_name
        return "NOISE"

    def _avg_entry_time(self, trades: list) -> Optional[float]:
        times = [t.minutes_after_launch for t, c in trades if t.minutes_after_launch is not None]
        return round(sum(times) / len(times), 1) if times else None

    def _avg_roi(self, trades: list) -> Optional[float]:
        rois = [t.roi for t, c in trades if t.roi is not None]
        return round(sum(rois) / len(rois), 2) if rois else None

    def _raw_win_rate(self, trades: list) -> Optional[float]:
        rois = [t.roi for t, c in trades if t.roi is not None]
        if not rois:
            return None
        return round(sum(1 for r in rois if r > 0) / len(rois), 3)
