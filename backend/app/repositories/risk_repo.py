from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.risk_metric import RiskMetric


class RiskMetricRepository:
    @staticmethod
    def save_metrics(db: Session, portfolio_id: int, **kwargs) -> RiskMetric:
        metric = RiskMetric(portfolio_id=portfolio_id, **kwargs)
        db.add(metric)
        db.commit()
        db.refresh(metric)
        return metric

    @staticmethod
    def get_latest_for_portfolio(db: Session, portfolio_id: int) -> RiskMetric | None:
        stmt = (
            select(RiskMetric)
            .where(RiskMetric.portfolio_id == portfolio_id)
            .order_by(RiskMetric.computed_at.desc())
            .limit(1)
        )
        return db.scalars(stmt).first()
