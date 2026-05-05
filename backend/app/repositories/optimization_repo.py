from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.optimization_result import OptimizationResult


class OptimizationResultRepository:
    @staticmethod
    def save_result(
        db: Session,
        portfolio_id: int,
        method: str,
        weights: dict,
        expected_return: float,
        volatility: float,
        sharpe_ratio: float,
        parameters: dict | None = None,
    ) -> OptimizationResult:
        result = OptimizationResult(
            portfolio_id=portfolio_id,
            method=method,
            weights=weights,
            expected_return=expected_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            parameters=parameters,
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        return result

    @staticmethod
    def get_by_portfolio(db: Session, portfolio_id: int) -> list[OptimizationResult]:
        stmt = (
            select(OptimizationResult)
            .where(OptimizationResult.portfolio_id == portfolio_id)
            .order_by(OptimizationResult.created_at.desc())
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_history(
        db: Session, portfolio_id: int, limit: int = 10
    ) -> list[OptimizationResult]:
        stmt = (
            select(OptimizationResult)
            .where(OptimizationResult.portfolio_id == portfolio_id)
            .order_by(OptimizationResult.created_at.desc())
            .limit(limit)
        )
        return list(db.scalars(stmt).all())
