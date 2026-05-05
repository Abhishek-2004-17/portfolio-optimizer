from datetime import datetime

from sqlalchemy import CHAR, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PortfolioAsset(Base):
    __tablename__ = "portfolio_assets"
    __table_args__ = (UniqueConstraint("portfolio_id", "ticker"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE"), index=True
    )
    ticker: Mapped[str] = mapped_column(String(20))
    weight: Mapped[float | None] = mapped_column(Numeric(8, 6))
    shares: Mapped[float | None] = mapped_column(Numeric(18, 6))
    purchase_price: Mapped[float | None] = mapped_column(Numeric(18, 4))
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    portfolio: Mapped["Portfolio"] = relationship(back_populates="assets")
