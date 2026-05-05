from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.models.portfolio_asset import PortfolioAsset
from app.schemas.suggestion import SuggestionResponse


TEMPLATES = {
    "conservative": {
        "VTI": 0.30, "BND": 0.30, "VXUS": 0.15, "AGG": 0.15, "GLD": 0.10,
    },
    "moderate": {
        "VTI": 0.35, "VXUS": 0.20, "BND": 0.15, "QQQ": 0.15, "GLD": 0.05, "VNQ": 0.10,
    },
    "aggressive": {
        "QQQ": 0.30, "VTI": 0.20, "VXUS": 0.15, "ARKK": 0.10, "TSLA": 0.10,
        "NVDA": 0.10, "BITO": 0.05,
    },
}


class SuggestionService:
    @staticmethod
    def suggest_by_profile(risk_profile: str, capital: float) -> dict:
        template = TEMPLATES.get(risk_profile, TEMPLATES["moderate"])
        allocations = {ticker: weight * capital for ticker, weight in template.items()}
        return {"profile": risk_profile, "weights": template, "allocations": allocations}

    @staticmethod
    def check_diversification(db: Session, portfolio_id: int) -> dict:
        assets = db.scalars(
            select(PortfolioAsset).where(PortfolioAsset.portfolio_id == portfolio_id)
        ).all()

        if not assets:
            return {
                "herfindahl_index": 0.0,
                "max_weight": 0.0,
                "max_weight_ticker": "",
                "suggestions": [SuggestionResponse(severity="warning", message="Portfolio has no assets")],
            }

        weights = [float(a.weight) for a in assets if a.weight is not None]
        if not weights:
            weights = [1.0 / len(assets)] * len(assets)

        hhi = sum(w ** 2 for w in weights)
        max_w = max(weights)
        max_ticker = assets[weights.index(max_w)].ticker

        suggestions = []
        if max_w > 0.40:
            suggestions.append(
                SuggestionResponse(
                    severity="danger",
                    message=f"High concentration: {max_ticker} has {max_w:.0%} weight",
                    detail="Consider reducing to below 30% for better diversification",
                )
            )
        if hhi > 0.25:
            suggestions.append(
                SuggestionResponse(
                    severity="warning",
                    message="Portfolio is concentrated (HHI > 0.25)",
                    detail="Herfindahl index indicates low diversification",
                )
            )
        if len(assets) < 5:
            suggestions.append(
                SuggestionResponse(
                    severity="info",
                    message=f"Only {len(assets)} assets — consider adding more",
                    detail="5-20 assets typically provide good diversification",
                )
            )

        return {
            "herfindahl_index": hhi,
            "max_weight": max_w,
            "max_weight_ticker": max_ticker,
            "suggestions": suggestions,
        }

    @staticmethod
    def rebalance_hints(db: Session, portfolio_id: int, threshold: float = 0.05) -> dict:
        from app.models.optimization_result import OptimizationResult

        assets = db.scalars(
            select(PortfolioAsset).where(PortfolioAsset.portfolio_id == portfolio_id)
        ).all()

        last_opt = db.scalars(
            select(OptimizationResult)
            .where(OptimizationResult.portfolio_id == portfolio_id)
            .order_by(OptimizationResult.created_at.desc())
            .limit(1)
        ).first()

        if not last_opt or not assets:
            return {
                "drift_items": [],
                "needs_rebalance": False,
                "suggestions": [
                    SuggestionResponse(severity="info", message="No optimization to compare against")
                ],
            }

        opt_weights = last_opt.weights
        drift_items = []
        needs_rebalance = False

        for asset in assets:
            current_w = float(asset.weight) if asset.weight else 0
            target_w = opt_weights.get(asset.ticker, 0)
            drift = abs(current_w - target_w)
            if drift > threshold:
                needs_rebalance = True
                drift_items.append({
                    "ticker": asset.ticker,
                    "current_weight": current_w,
                    "target_weight": target_w,
                    "drift": drift,
                })

        suggestions = []
        if needs_rebalance:
            suggestions.append(
                SuggestionResponse(
                    severity="warning",
                    message="Portfolio drift detected — rebalancing recommended",
                    detail=f"{len(drift_items)} asset(s) have drifted more than {threshold:.0%}",
                )
            )

        return {
            "drift_items": drift_items,
            "needs_rebalance": needs_rebalance,
            "suggestions": suggestions,
        }
