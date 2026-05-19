from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base


class Ticker(Base):
    """Model for storing ticker information."""

    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    sector = Column(String(100), nullable=True)
    exchange = Column(String(50), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Ticker(symbol={self.symbol}, name={self.name})>"
