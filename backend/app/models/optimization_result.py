from datetime import datetime

from sqlalchemy import DateTime, Double, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OptimizationResult(Base):
    __tablename__ = "optimization_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE"), index=True
    )
    method: Mapped[str] = mapped_column(String(32))
    weights: Mapped[dict] = mapped_column(JSONB)
    expected_return: Mapped[float] = mapped_column(Double)
    volatility: Mapped[float] = mapped_column(Double)
    sharpe_ratio: Mapped[float] = mapped_column(Double)
    parameters: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    portfolio: Mapped["Portfolio"] = relationship(back_populates="optimizations")
