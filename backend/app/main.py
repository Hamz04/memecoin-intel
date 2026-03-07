"""
FastAPI application entry point for the Memecoin Insider Intelligence Platform.
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./memecoin_intel.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create tables and seed data on startup."""
    logger.info("Starting Memecoin Insider Intelligence Platform...")
    Base.metadata.create_all(bind=engine)

    # Seed coins
    db = SessionLocal()
    try:
        from app.seed_data import seed_coins
        added = seed_coins(db)
        if added:
            logger.info(f"Seeded {added} memecoins into database")
    finally:
        db.close()

    yield
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Memecoin Insider Intelligence",
    description="Track recurring insider wallets across 49+ memecoins",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.routes.insiders import router as insiders_router
from app.routes.coins import router as coins_router
from app.routes.alerts import router as alerts_router

app.include_router(insiders_router)
app.include_router(coins_router)
app.include_router(alerts_router)


@app.get("/")
def root():
    return {
        "name": "Memecoin Insider Intelligence Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "stats": "/api/stats",
            "leaderboard": "/api/insiders/leaderboard",
            "coins": "/api/coins",
            "alerts": "/api/alerts/feed",
        },
    }


@app.get("/health")
def health():
    return {"status": "ok"}
