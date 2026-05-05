from datetime import datetime

from sqlalchemy import DateTime, Double, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RiskMetric(Base):
    __tablename__ = "risk_metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE"), index=True
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # VaR — Historical
    var_historical_95: Mapped[float | None] = mapped_column(Double)
    var_historical_99: Mapped[float | None] = mapped_column(Double)
    # VaR — Parametric
    var_parametric_95: Mapped[float | None] = mapped_column(Double)
    var_parametric_99: Mapped[float | None] = mapped_column(Double)
    # VaR — Monte Carlo
    var_montecarlo_95: Mapped[float | None] = mapped_column(Double)
    var_montecarlo_99: Mapped[float | None] = mapped_column(Double)
    # CVaR — Historical
    cvar_historical_95: Mapped[float | None] = mapped_column(Double)
    cvar_historical_99: Mapped[float | None] = mapped_column(Double)
    # CVaR — Parametric
    cvar_parametric_95: Mapped[float | None] = mapped_column(Double)
    cvar_parametric_99: Mapped[float | None] = mapped_column(Double)
    # CVaR — Monte Carlo
    cvar_montecarlo_95: Mapped[float | None] = mapped_column(Double)
    cvar_montecarlo_99: Mapped[float | None] = mapped_column(Double)

    max_drawdown: Mapped[float | None] = mapped_column(Double)
    sharpe_ratio: Mapped[float | None] = mapped_column(Double)
    sortino_ratio: Mapped[float | None] = mapped_column(Double)
    beta: Mapped[float | None] = mapped_column(Double)
    annualised_return: Mapped[float | None] = mapped_column(Double)
    annualised_volatility: Mapped[float | None] = mapped_column(Double)
    correlation_matrix: Mapped[dict | None] = mapped_column(JSONB)

    portfolio: Mapped["Portfolio"] = relationship(back_populates="risk_metrics")
