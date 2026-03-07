"""
SQLAlchemy models for the Memecoin Insider Intelligence Platform.
6 tables: coins, wallets, trades, insider_scores, alerts, subscriptions.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text,
    ForeignKey, JSON, Index
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Coin(Base):
    """Tracked memecoin with contract address and chain info."""
    __tablename__ = "coins"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    chain = Column(String(20), nullable=False)
    contract_address = Column(String(100), nullable=False, unique=True)
    launch_date = Column(DateTime, nullable=True)
    peak_market_cap = Column(Float, nullable=True)
    current_market_cap = Column(Float, nullable=True)
    dune_query_id = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trades = relationship("Trade", back_populates="coin", lazy="dynamic")
    alerts = relationship("Alert", back_populates="coin", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "name": self.name,
            "chain": self.chain,
            "contract_address": self.contract_address,
            "launch_date": self.launch_date.isoformat() if self.launch_date else None,
            "peak_market_cap": self.peak_market_cap,
            "current_market_cap": self.current_market_cap,
            "is_active": self.is_active,
        }


class Wallet(Base):
    """Tracked wallet address with cross-chain identity."""
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True)
    address = Column(String(100), nullable=False, unique=True, index=True)
    chain = Column(String(20), nullable=False)
    label = Column(String(100), nullable=True)
    first_seen = Column(DateTime, nullable=True)
    total_coins_hit = Column(Integer, default=0)
    total_trades = Column(Integer, default=0)
    avg_entry_time_minutes = Column(Float, nullable=True)
    avg_roi = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=True)
    is_flagged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trades = relationship("Trade", back_populates="wallet", lazy="dynamic")
    insider_score = relationship("InsiderScore", back_populates="wallet", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "address": self.address,
            "chain": self.chain,
            "label": self.label,
            "total_coins_hit": self.total_coins_hit,
            "total_trades": self.total_trades,
            "avg_entry_time_minutes": self.avg_entry_time_minutes,
            "avg_roi": self.avg_roi,
            "win_rate": self.win_rate,
            "is_flagged": self.is_flagged,
        }


class Trade(Base):
    """Individual trade record linking wallet to coin."""
    __tablename__ = "trades"
    __table_args__ = (
        Index("ix_trades_wallet_coin", "wallet_id", "coin_id"),
    )

    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    coin_id = Column(Integer, ForeignKey("coins.id"), nullable=False)
    tx_hash = Column(String(100), nullable=True, unique=True)
    trade_type = Column(String(10), nullable=False)
    amount_tokens = Column(Float, nullable=True)
    amount_usd = Column(Float, nullable=True)
    price_at_trade = Column(Float, nullable=True)
    market_cap_at_trade = Column(Float, nullable=True)
    minutes_after_launch = Column(Float, nullable=True)
    roi = Column(Float, nullable=True)
    block_number = Column(Integer, nullable=True)
    traded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    wallet = relationship("Wallet", back_populates="trades")
    coin = relationship("Coin", back_populates="trades")

    def to_dict(self):
        return {
            "id": self.id,
            "wallet_address": self.wallet.address if self.wallet else None,
            "coin_symbol": self.coin.symbol if self.coin else None,
            "trade_type": self.trade_type,
            "amount_usd": self.amount_usd,
            "price_at_trade": self.price_at_trade,
            "market_cap_at_trade": self.market_cap_at_trade,
            "minutes_after_launch": self.minutes_after_launch,
            "roi": self.roi,
            "traded_at": self.traded_at.isoformat() if self.traded_at else None,
        }


class InsiderScore(Base):
    """Computed insider score for a wallet (0-100)."""
    __tablename__ = "insider_scores"

    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False, unique=True)
    score = Column(Float, nullable=False, default=0, index=True)
    tier = Column(String(20), nullable=False, default="NOISE")
    coins_hit_score = Column(Float, default=0)
    win_rate_score = Column(Float, default=0)
    entry_speed_score = Column(Float, default=0)
    roi_score = Column(Float, default=0)
    mcap_impact_score = Column(Float, default=0)
    behavioral_flags = Column(JSON, nullable=True)
    coins_list = Column(JSON, nullable=True)
    last_computed = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    wallet = relationship("Wallet", back_populates="insider_score")

    def to_dict(self):
        return {
            "wallet_address": self.wallet.address if self.wallet else None,
            "score": round(self.score, 1),
            "tier": self.tier,
            "coins_hit_score": round(self.coins_hit_score, 1),
            "win_rate_score": round(self.win_rate_score, 1),
            "entry_speed_score": round(self.entry_speed_score, 1),
            "roi_score": round(self.roi_score, 1),
            "mcap_impact_score": round(self.mcap_impact_score, 1),
            "behavioral_flags": self.behavioral_flags or [],
            "coins_list": self.coins_list or [],
            "last_computed": self.last_computed.isoformat() if self.last_computed else None,
        }


class Alert(Base):
    """Real-time alert when tracked insider makes a move."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    coin_id = Column(Integer, ForeignKey("coins.id"), nullable=True)
    alert_type = Column(String(30), nullable=False)
    severity = Column(String(10), nullable=False, default="MEDIUM")
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    is_read = Column(Boolean, default=False)
    telegram_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    wallet = relationship("Wallet")
    coin = relationship("Coin", back_populates="alerts")

    def to_dict(self):
        return {
            "id": self.id,
            "wallet_address": self.wallet.address if self.wallet else None,
            "coin_symbol": self.coin.symbol if self.coin else None,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "metadata": self.metadata,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Subscription(Base):
    """User subscription managed via Stripe."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    email = Column(String(200), nullable=False, unique=True, index=True)
    stripe_customer_id = Column(String(100), nullable=True)
    stripe_subscription_id = Column(String(100), nullable=True)
    tier = Column(String(20), nullable=False, default="FREE")
    status = Column(String(20), nullable=False, default="active")
    telegram_chat_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "tier": self.tier,
            "status": self.status,
            "has_telegram": bool(self.telegram_chat_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
