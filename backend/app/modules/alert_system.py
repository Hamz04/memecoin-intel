"""
Alert System: Monitors tracked insider wallets for new activity and generates
alerts. Supports real-time notifications via Telegram for Elite subscribers.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models import Wallet, Trade, Coin, InsiderScore, Alert, Subscription

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


class AlertSystem:
    """Generates and manages alerts for insider wallet activity."""

    def __init__(self, db: Session):
        self.db = db
        self.http = httpx.AsyncClient(timeout=10)

    async def close(self):
        await self.http.aclose()

    # ------------------------------------------------------------------
    # Alert generation
    # ------------------------------------------------------------------
    def check_for_new_alerts(self) -> list:
        """Scan recent trades and generate alerts for notable activity."""
        new_alerts = []
        cutoff = datetime.utcnow() - timedelta(hours=1)

        # Get recent trades from scored wallets
        recent_trades = (
            self.db.query(Trade, Wallet, Coin, InsiderScore)
            .join(Wallet, Trade.wallet_id == Wallet.id)
            .join(Coin, Trade.coin_id == Coin.id)
            .join(InsiderScore, InsiderScore.wallet_id == Wallet.id)
            .filter(Trade.created_at >= cutoff)
            .filter(InsiderScore.score >= 30)
            .order_by(desc(Trade.created_at))
            .all()
        )

        for trade, wallet, coin, score in recent_trades:
            # Check if alert already exists for this trade
            existing = (
                self.db.query(Alert)
                .filter(Alert.wallet_id == wallet.id)
                .filter(Alert.coin_id == coin.id)
                .filter(Alert.created_at >= cutoff)
                .first()
            )
            if existing:
                continue

            alert = self._create_alert(trade, wallet, coin, score)
            if alert:
                self.db.add(alert)
                new_alerts.append(alert)

        self.db.commit()
        return new_alerts

    def _create_alert(self, trade, wallet, coin, score) -> Optional[Alert]:
        """Create an alert based on trade characteristics."""
        if trade.trade_type == "BUY":
            severity = self._calculate_severity(score.score, trade)
            alert = Alert(
                wallet_id=wallet.id,
                coin_id=coin.id,
                alert_type="NEW_BUY",
                severity=severity,
                title=f"{score.tier} insider bought {coin.symbol}",
                description=(
                    f"Wallet {wallet.address[:8]}...{wallet.address[-6:]} "
                    f"(score: {score.score:.0f}) bought {coin.symbol} on {coin.chain}. "
                    f"Amount: ${trade.amount_usd:,.0f}" if trade.amount_usd else
                    f"Wallet {wallet.address[:8]}...{wallet.address[-6:]} "
                    f"(score: {score.score:.0f}) bought {coin.symbol} on {coin.chain}."
                ),
                metadata={
                    "wallet_score": score.score,
                    "wallet_tier": score.tier,
                    "trade_amount_usd": trade.amount_usd,
                    "coin_chain": coin.chain,
                    "minutes_after_launch": trade.minutes_after_launch,
                },
            )
            return alert

        elif trade.trade_type == "SELL" and trade.amount_usd and trade.amount_usd > 100000:
            alert = Alert(
                wallet_id=wallet.id,
                coin_id=coin.id,
                alert_type="LARGE_SELL",
                severity="HIGH",
                title=f"Large sell by {score.tier} insider on {coin.symbol}",
                description=(
                    f"Wallet {wallet.address[:8]}...{wallet.address[-6:]} "
                    f"sold ${trade.amount_usd:,.0f} of {coin.symbol}."
                ),
                metadata={
                    "wallet_score": score.score,
                    "trade_amount_usd": trade.amount_usd,
                },
            )
            return alert

        return None

    def _calculate_severity(self, score: float, trade) -> str:
        """Determine alert severity based on insider score and trade size."""
        if score >= 85:
            return "CRITICAL"
        elif score >= 70:
            return "HIGH"
        elif score >= 50:
            return "MEDIUM"
        return "LOW"

    # ------------------------------------------------------------------
    # Alert queries
    # ------------------------------------------------------------------
    def get_alert_feed(
        self, limit: int = 50, offset: int = 0,
        severity: Optional[str] = None, alert_type: Optional[str] = None
    ) -> list:
        """Get paginated alert feed with optional filters."""
        query = self.db.query(Alert).order_by(desc(Alert.created_at))

        if severity:
            query = query.filter(Alert.severity == severity.upper())
        if alert_type:
            query = query.filter(Alert.alert_type == alert_type.upper())

        alerts = query.offset(offset).limit(limit).all()
        return [a.to_dict() for a in alerts]

    def get_alert_stats(self) -> dict:
        """Get alert statistics for the dashboard."""
        total = self.db.query(func.count(Alert.id)).scalar() or 0
        last_24h = (
            self.db.query(func.count(Alert.id))
            .filter(Alert.created_at >= datetime.utcnow() - timedelta(hours=24))
            .scalar() or 0
        )
        critical = (
            self.db.query(func.count(Alert.id))
            .filter(Alert.severity == "CRITICAL")
            .filter(Alert.created_at >= datetime.utcnow() - timedelta(hours=24))
            .scalar() or 0
        )
        by_type = dict(
            self.db.query(Alert.alert_type, func.count(Alert.id))
            .group_by(Alert.alert_type)
            .all()
        )

        return {
            "total_alerts": total,
            "last_24h": last_24h,
            "critical_24h": critical,
            "by_type": by_type,
        }

    # ------------------------------------------------------------------
    # Telegram notifications
    # ------------------------------------------------------------------
    async def send_telegram_alerts(self, alerts: list):
        """Send alerts to Elite subscribers via Telegram."""
        if not TELEGRAM_BOT_TOKEN:
            logger.warning("TELEGRAM_BOT_TOKEN not set, skipping Telegram alerts")
            return

        elite_subs = (
            self.db.query(Subscription)
            .filter(Subscription.tier == "ELITE")
            .filter(Subscription.status == "active")
            .filter(Subscription.telegram_chat_id.isnot(None))
            .all()
        )

        if not elite_subs:
            return

        for alert in alerts:
            if alert.severity not in ("CRITICAL", "HIGH"):
                continue

            message = self._format_telegram_message(alert)
            for sub in elite_subs:
                await self._send_telegram_message(sub.telegram_chat_id, message)
                alert.telegram_sent = True

        self.db.commit()

    def _format_telegram_message(self, alert: Alert) -> str:
        """Format alert as a Telegram message."""
        severity_emoji = {
            "CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "📊", "LOW": "ℹ️"
        }
        emoji = severity_emoji.get(alert.severity, "📊")
        return (
            f"{emoji} *{alert.title}*\n\n"
            f"{alert.description}\n\n"
            f"Severity: {alert.severity}\n"
            f"Time: {alert.created_at.strftime('%Y-%m-%d %H:%M UTC')}"
        )

    async def _send_telegram_message(self, chat_id: str, text: str):
        """Send a message via Telegram Bot API."""
        try:
            url = f"{TELEGRAM_API_BASE}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
            }
            resp = await self.http.post(url, json=payload)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
