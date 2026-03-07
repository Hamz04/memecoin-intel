"""
Insider routes: Leaderboard, wallet detail, overlap map.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.models import Wallet, InsiderScore, Trade, Coin
from app.modules.cross_reference import CrossReferenceEngine
from app.main import get_db

router = APIRouter(prefix="/api/insiders", tags=["insiders"])


@router.get("/leaderboard")
def get_leaderboard(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    min_score: float = Query(0, ge=0, le=100),
    tier: str = Query(None),
    db: Session = Depends(get_db),
):
    """Get ranked insider wallets by score."""
    query = (
        db.query(InsiderScore, Wallet)
        .join(Wallet, InsiderScore.wallet_id == Wallet.id)
        .filter(InsiderScore.score >= min_score)
    )

    if tier:
        query = query.filter(InsiderScore.tier == tier.upper())

    query = query.order_by(InsiderScore.score.desc())
    total = query.count()
    results = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "wallets": [
            {
                **score.to_dict(),
                "address": wallet.address,
                "chain": wallet.chain,
                "label": wallet.label,
                "total_trades": wallet.total_trades,
                "is_flagged": wallet.is_flagged,
            }
            for score, wallet in results
        ],
    }


@router.get("/wallet/{address}")
def get_wallet_detail(address: str, db: Session = Depends(get_db)):
    """Deep dive into a specific wallet."""
    wallet = db.query(Wallet).filter(Wallet.address == address).first()
    if not wallet:
        return {"error": "Wallet not found"}

    score = db.query(InsiderScore).filter(InsiderScore.wallet_id == wallet.id).first()

    trades = (
        db.query(Trade, Coin)
        .join(Coin, Trade.coin_id == Coin.id)
        .filter(Trade.wallet_id == wallet.id)
        .order_by(Trade.traded_at.desc())
        .limit(100)
        .all()
    )

    engine = CrossReferenceEngine(db)
    connections = engine.find_wallet_connections(address)

    return {
        "wallet": wallet.to_dict(),
        "score": score.to_dict() if score else None,
        "trades": [trade.to_dict() for trade, coin in trades],
        "connections": connections.get("connections", []),
    }


@router.get("/overlap-map")
def get_overlap_map(
    min_score: int = Query(50, ge=0, le=100),
    db: Session = Depends(get_db),
):
    """Get cross-reference overlap map for visualization."""
    engine = CrossReferenceEngine(db)
    overlap = engine.get_overlap_map(min_score=min_score)

    return {
        "min_score": min_score,
        "coins": len(overlap),
        "map": overlap,
    }
