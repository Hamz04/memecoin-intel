"""
Alert routes: Alert feed, stats, and subscription management.
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.models import Subscription
from app.modules.alert_system import AlertSystem
from app.modules.subscription import SubscriptionManager
from app.main import get_db

router = APIRouter(prefix="/api", tags=["alerts"])


@router.get("/alerts/feed")
def get_alert_feed(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    severity: str = Query(None),
    alert_type: str = Query(None),
    db: Session = Depends(get_db),
):
    """Get paginated alert feed with optional filters."""
    system = AlertSystem(db)
    alerts = system.get_alert_feed(
        limit=limit, offset=offset,
        severity=severity, alert_type=alert_type
    )
    stats = system.get_alert_stats()

    return {
        "alerts": alerts,
        "stats": stats,
        "limit": limit,
        "offset": offset,
    }


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get overview statistics for the dashboard."""
    from sqlalchemy import func
    from app.models import Wallet, Coin, InsiderScore, Alert
    from datetime import datetime, timedelta

    total_coins = db.query(func.count(Coin.id)).filter(Coin.is_active == True).scalar() or 0
    total_wallets = db.query(func.count(Wallet.id)).scalar() or 0
    total_scored = db.query(func.count(InsiderScore.id)).scalar() or 0
    legendary = (
        db.query(func.count(InsiderScore.id))
        .filter(InsiderScore.tier == "LEGENDARY")
        .scalar() or 0
    )
    elite = (
        db.query(func.count(InsiderScore.id))
        .filter(InsiderScore.tier == "ELITE")
        .scalar() or 0
    )

    alert_system = AlertSystem(db)
    alert_stats = alert_system.get_alert_stats()

    return {
        "total_coins_tracked": total_coins,
        "total_wallets": total_wallets,
        "total_scored_wallets": total_scored,
        "legendary_insiders": legendary,
        "elite_insiders": elite,
        "alerts": alert_stats,
    }


@router.post("/subscribe/checkout")
async def create_checkout(request: Request, db: Session = Depends(get_db)):
    """Create a Stripe checkout session."""
    body = await request.json()
    email = body.get("email")
    tier = body.get("tier", "PRO").upper()
    success_url = body.get("success_url", "http://localhost:3000/success")
    cancel_url = body.get("cancel_url", "http://localhost:3000/pricing")

    if not email:
        return {"error": "Email is required"}

    manager = SubscriptionManager(db)
    url = manager.create_checkout_session(email, tier, success_url, cancel_url)

    if url:
        return {"checkout_url": url}
    return {"error": "Failed to create checkout session"}


@router.post("/subscribe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    manager = SubscriptionManager(db)
    result = manager.handle_webhook(payload, sig_header)

    return result


@router.get("/scan/trigger")
async def trigger_scan(db: Session = Depends(get_db)):
    """Manually trigger a chain scan and scoring update."""
    from app.modules.insider_scorer import InsiderScorer

    scorer = InsiderScorer(db)
    results = scorer.score_all_wallets()

    alert_system = AlertSystem(db)
    new_alerts = alert_system.check_for_new_alerts()

    return {
        "wallets_scored": len(results),
        "new_alerts": len(new_alerts),
        "message": "Scan complete",
    }
