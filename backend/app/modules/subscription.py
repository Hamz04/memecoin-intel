"""
Subscription Manager: Handles Stripe payment integration for
Free / Pro ($49/mo) / Elite ($199/mo) tiers.
"""

import os
import logging
from typing import Optional

import stripe
from sqlalchemy.orm import Session

from app.models import Subscription

logger = logging.getLogger(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

PRICE_IDS = {
    "PRO": os.getenv("STRIPE_PRO_PRICE_ID", "price_pro_monthly"),
    "ELITE": os.getenv("STRIPE_ELITE_PRICE_ID", "price_elite_monthly"),
}

TIER_LIMITS = {
    "FREE": {
        "max_insiders": 5,
        "min_score": 85,
        "early_buyers_per_coin": 10,
        "overlap_map": False,
        "alerts": "limited",
        "telegram": False,
        "behavioral_flags": False,
        "api_access": False,
    },
    "PRO": {
        "max_insiders": None,  # Unlimited
        "min_score": 50,
        "early_buyers_per_coin": 100,
        "overlap_map": True,
        "alerts": "full",
        "telegram": False,
        "behavioral_flags": False,
        "api_access": False,
    },
    "ELITE": {
        "max_insiders": None,
        "min_score": 30,
        "early_buyers_per_coin": 500,
        "overlap_map": True,
        "alerts": "full",
        "telegram": True,
        "behavioral_flags": True,
        "api_access": True,
    },
}


class SubscriptionManager:
    """Manages user subscriptions and Stripe integration."""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_subscription(self, email: str) -> Subscription:
        """Get existing subscription or create a free one."""
        sub = self.db.query(Subscription).filter(Subscription.email == email).first()
        if not sub:
            sub = Subscription(email=email, tier="FREE", status="active")
            self.db.add(sub)
            self.db.commit()
        return sub

    def get_tier_limits(self, email: str) -> dict:
        """Get the feature limits for a user's current tier."""
        sub = self.get_or_create_subscription(email)
        limits = TIER_LIMITS.get(sub.tier, TIER_LIMITS["FREE"]).copy()
        limits["tier"] = sub.tier
        limits["status"] = sub.status
        return limits

    # ------------------------------------------------------------------
    # Stripe Checkout
    # ------------------------------------------------------------------
    def create_checkout_session(
        self, email: str, tier: str, success_url: str, cancel_url: str
    ) -> Optional[str]:
        """Create a Stripe Checkout session and return the URL."""
        if tier not in PRICE_IDS:
            logger.error(f"Invalid tier: {tier}")
            return None

        if not stripe.api_key:
            logger.error("STRIPE_SECRET_KEY not set")
            return None

        try:
            sub = self.get_or_create_subscription(email)

            # Create or retrieve Stripe customer
            if not sub.stripe_customer_id:
                customer = stripe.Customer.create(email=email)
                sub.stripe_customer_id = customer.id
                self.db.commit()

            session = stripe.checkout.Session.create(
                customer=sub.stripe_customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price": PRICE_IDS[tier],
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={"tier": tier, "email": email},
            )

            return session.url

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return None

    # ------------------------------------------------------------------
    # Stripe Webhook
    # ------------------------------------------------------------------
    def handle_webhook(self, payload: bytes, sig_header: str) -> dict:
        """Process Stripe webhook events."""
        if not STRIPE_WEBHOOK_SECRET:
            return {"error": "Webhook secret not configured"}

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            return {"error": str(e)}

        event_type = event["type"]
        data = event["data"]["object"]

        if event_type == "checkout.session.completed":
            self._handle_checkout_complete(data)
        elif event_type == "customer.subscription.updated":
            self._handle_subscription_update(data)
        elif event_type == "customer.subscription.deleted":
            self._handle_subscription_deleted(data)

        return {"status": "ok", "event_type": event_type}

    def _handle_checkout_complete(self, session_data: dict):
        """Handle successful checkout."""
        email = session_data.get("metadata", {}).get("email")
        tier = session_data.get("metadata", {}).get("tier", "PRO")
        subscription_id = session_data.get("subscription")

        if email:
            sub = self.get_or_create_subscription(email)
            sub.tier = tier
            sub.stripe_subscription_id = subscription_id
            sub.status = "active"
            self.db.commit()
            logger.info(f"Subscription activated: {email} -> {tier}")

    def _handle_subscription_update(self, sub_data: dict):
        """Handle subscription changes."""
        stripe_sub_id = sub_data.get("id")
        status = sub_data.get("status")

        sub = (
            self.db.query(Subscription)
            .filter(Subscription.stripe_subscription_id == stripe_sub_id)
            .first()
        )
        if sub:
            sub.status = status
            self.db.commit()

    def _handle_subscription_deleted(self, sub_data: dict):
        """Handle subscription cancellation."""
        stripe_sub_id = sub_data.get("id")
        sub = (
            self.db.query(Subscription)
            .filter(Subscription.stripe_subscription_id == stripe_sub_id)
            .first()
        )
        if sub:
            sub.tier = "FREE"
            sub.status = "canceled"
            sub.stripe_subscription_id = None
            self.db.commit()
            logger.info(f"Subscription canceled: {sub.email}")
