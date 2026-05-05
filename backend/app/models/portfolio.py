from sqlalchemy import CHAR, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Portfolio(Base, TimestampMixin):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    base_currency: Mapped[str] = mapped_column(CHAR(3), default="USD")
    initial_capital: Mapped[float] = mapped_column(Numeric(18, 2))

    assets: Mapped[list["PortfolioAsset"]] = relationship(
        back_populates="portfolio", cascade="all, delete-orphan"
    )
    optimizations: Mapped[list["OptimizationResult"]] = relationship(
        back_populates="portfolio", cascade="all, delete-orphan"
    )
    risk_metrics: Mapped[list["RiskMetric"]] = relationship(
        back_populates="portfolio", cascade="all, delete-orphan"
    )
