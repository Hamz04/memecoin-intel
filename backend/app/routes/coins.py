"""
Coin routes: List tracked memecoins and per-coin forensic analysis.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Coin, Trade, Wallet, InsiderScore
from app.main import get_db

router = APIRouter(prefix="/api/coins", tags=["coins"])


@router.get("")
def list_coins(
    chain: str = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List all tracked memecoins with optional chain filter."""
    query = db.query(Coin).filter(Coin.is_active == True)

    if chain:
        query = query.filter(Coin.chain == chain.upper())

    total = query.count()
    coins = query.order_by(Coin.peak_market_cap.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "coins": [coin.to_dict() for coin in coins],
    }


@router.get("/{symbol}/forensics")
def get_coin_forensics(
    symbol: str,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Forensic analysis of early buyers for a specific coin."""
    coin = db.query(Coin).filter(Coin.symbol == symbol.upper()).first()
    if not coin:
        return {"error": "Coin not found"}

    # Get early buyers with their insider scores
    early_buyers = (
        db.query(Trade, Wallet, InsiderScore)
        .join(Wallet, Trade.wallet_id == Wallet.id)
        .outerjoin(InsiderScore, InsiderScore.wallet_id == Wallet.id)
        .filter(Trade.coin_id == coin.id)
        .filter(Trade.trade_type == "BUY")
        .order_by(Trade.minutes_after_launch.asc())
        .limit(limit)
        .all()
    )

    # Stats
    total_early = len(early_buyers)
    scored_buyers = [b for b in early_buyers if b[2] and b[2].score >= 50]
    avg_score = (
        sum(b[2].score for b in scored_buyers) / len(scored_buyers)
        if scored_buyers else 0
    )

    return {
        "coin": coin.to_dict(),
        "total_early_buyers": total_early,
        "notable_insiders": len(scored_buyers),
        "avg_insider_score": round(avg_score, 1),
        "early_buyers": [
            {
                "address": wallet.address,
                "chain": wallet.chain,
                "minutes_after_launch": round(trade.minutes_after_launch, 1) if trade.minutes_after_launch else None,
                "amount_usd": trade.amount_usd,
                "roi": round(trade.roi, 2) if trade.roi else None,
                "insider_score": round(score.score, 1) if score else None,
                "insider_tier": score.tier if score else None,
            }
            for trade, wallet, score in early_buyers
        ],
    }
