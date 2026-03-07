"""
Telegram Bot for Elite tier subscribers.
Sends real-time alerts when tracked insiders make moves.
Also supports commands: /start, /status, /top, /alerts
"""

import os
import logging
import asyncio

import httpx
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from app.models import Base, InsiderScore, Wallet, Alert, Subscription

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./memecoin_intel.db")
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


async def send_message(chat_id: str, text: str):
    """Send a message via Telegram."""
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{API_BASE}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            )
        except Exception as e:
            logger.error(f"Send error: {e}")


async def handle_update(update: dict):
    """Process incoming Telegram update."""
    message = update.get("message", {})
    chat_id = str(message.get("chat", {}).get("id", ""))
    text = message.get("text", "").strip()

    if not chat_id or not text:
        return

    if text == "/start":
        await send_message(chat_id, (
            "*Memecoin Insider Intelligence Bot*\n\n"
            "Get real-time alerts when tracked insiders make moves.\n\n"
            "Commands:\n"
            "/status - Your subscription status\n"
            "/top - Top 5 insiders right now\n"
            "/alerts - Recent critical alerts\n\n"
            "Link your account at the web dashboard to activate alerts."
        ))

    elif text == "/status":
        db = SessionLocal()
        sub = db.query(Subscription).filter(
            Subscription.telegram_chat_id == chat_id
        ).first()
        db.close()

        if sub:
            await send_message(chat_id, (
                f"*Subscription Status*\n\n"
                f"Email: {sub.email}\n"
                f"Tier: {sub.tier}\n"
                f"Status: {sub.status}"
            ))
        else:
            await send_message(chat_id, (
                "No subscription linked to this chat.\n"
                "Link your account at the web dashboard."
            ))

    elif text == "/top":
        db = SessionLocal()
        top = (
            db.query(InsiderScore, Wallet)
            .join(Wallet, InsiderScore.wallet_id == Wallet.id)
            .order_by(desc(InsiderScore.score))
            .limit(5)
            .all()
        )
        db.close()

        if top:
            lines = ["*Top 5 Insiders*\n"]
            for i, (score, wallet) in enumerate(top, 1):
                addr = f"{wallet.address[:6]}...{wallet.address[-4:]}"
                lines.append(
                    f"{i}. {addr} - Score: {score.score:.0f} ({score.tier})\n"
                    f"   Coins: {', '.join(score.coins_list or [])}"
                )
            await send_message(chat_id, "\n".join(lines))
        else:
            await send_message(chat_id, "No scored wallets yet.")

    elif text == "/alerts":
        db = SessionLocal()
        alerts = (
            db.query(Alert)
            .filter(Alert.severity.in_(["CRITICAL", "HIGH"]))
            .order_by(desc(Alert.created_at))
            .limit(5)
            .all()
        )
        db.close()

        if alerts:
            lines = ["*Recent Critical Alerts*\n"]
            for alert in alerts:
                lines.append(f"[{alert.severity}] {alert.title}")
            await send_message(chat_id, "\n".join(lines))
        else:
            await send_message(chat_id, "No recent critical alerts.")


async def poll_updates():
    """Long-poll for Telegram updates."""
    offset = 0
    async with httpx.AsyncClient(timeout=60) as client:
        while True:
            try:
                resp = await client.get(
                    f"{API_BASE}/getUpdates",
                    params={"offset": offset, "timeout": 30},
                )
                data = resp.json()
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    await handle_update(update)
            except Exception as e:
                logger.error(f"Poll error: {e}")
                await asyncio.sleep(5)


def main():
    """Run the Telegram bot."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    logger.info("Starting Telegram bot...")
    asyncio.run(poll_updates())


if __name__ == "__main__":
    main()
