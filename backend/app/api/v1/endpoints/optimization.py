from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.optimization_repo import OptimizationResultRepository
from app.schemas.optimization import (
    FrontierRequest,
    FrontierResponse,
    OptimizeRequest,
    OptimizeResponse,
    TargetReturnRequest,
    TargetRiskRequest,
)
from app.services.optimization_service import OptimizationService

router = APIRouter()


@router.post("/max-sharpe", response_model=OptimizeResponse)
def max_sharpe(body: OptimizeRequest, db: Session = Depends(get_db)):
    result = OptimizationService.max_sharpe(
        tickers=body.tickers,
        start_date=body.start_date,
        end_date=body.end_date,
        risk_free_rate=body.risk_free_rate,
        weight_bounds=body.weight_bounds,
        total_portfolio_value=body.total_portfolio_value,
    )

    if body.portfolio_id is not None:
        OptimizationResultRepository.save_result(
            db=db,
            portfolio_id=body.portfolio_id,
            method=result["method"],
            weights=result["weights"],
            expected_return=result["expected_return"],
            volatility=result["volatility"],
            sharpe_ratio=result["sharpe_ratio"],
            parameters={
                "risk_free_rate": body.risk_free_rate,
                "weight_bounds": list(body.weight_bounds),
                "start_date": body.start_date,
                "end_date": body.end_date,
            },
        )

    return result


@router.post("/min-volatility", response_model=OptimizeResponse)
def min_volatility(body: OptimizeRequest, db: Session = Depends(get_db)):
    result = OptimizationService.min_volatility(
        tickers=body.tickers,
        start_date=body.start_date,
        end_date=body.end_date,
        weight_bounds=body.weight_bounds,
    )

    if body.portfolio_id is not None:
        OptimizationResultRepository.save_result(
            db=db,
            portfolio_id=body.portfolio_id,
            method=result["method"],
            weights=result["weights"],
            expected_return=result["expected_return"],
            volatility=result["volatility"],
            sharpe_ratio=result["sharpe_ratio"],
            parameters={
                "weight_bounds": list(body.weight_bounds),
                "start_date": body.start_date,
                "end_date": body.end_date,
            },
        )

    return result


@router.post("/target-return", response_model=OptimizeResponse)
def target_return(body: TargetReturnRequest, db: Session = Depends(get_db)):
    result = OptimizationService.target_return(
        tickers=body.tickers,
        start_date=body.start_date,
        end_date=body.end_date,
        target_return=body.target_return,
        risk_free_rate=body.risk_free_rate,
        weight_bounds=body.weight_bounds,
    )

    return result


@router.post("/target-risk", response_model=OptimizeResponse)
def target_risk(body: TargetRiskRequest, db: Session = Depends(get_db)):
    try:
        result = OptimizationService.target_risk(
            tickers=body.tickers,
            start_date=body.start_date,
            end_date=body.end_date,
            target_volatility=body.target_volatility,
            risk_free_rate=body.risk_free_rate,
            weight_bounds=body.weight_bounds,
        )
    except (ValueError, Exception) as e:
        raise HTTPException(
            status_code=422,
            detail=str(e),
        )

    return result


@router.post("/efficient-frontier", response_model=FrontierResponse)
def efficient_frontier(body: FrontierRequest, db: Session = Depends(get_db)):
    from pypfopt.exceptions import OptimizationError
    try:
        result = OptimizationService.efficient_frontier(
            tickers=body.tickers,
            start_date=body.start_date,
            end_date=body.end_date,
            risk_free_rate=body.risk_free_rate,
            weight_bounds=body.weight_bounds,
            n_points=body.n_points,
            total_portfolio_value=body.total_portfolio_value,
        )
    except OptimizationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Optimization solver failed: {e}. Try different tickers or a wider date range.",
        )
    return result


@router.get("/portfolio/{portfolio_id}/history", response_model=list[OptimizeResponse])
def optimization_history(portfolio_id: int, db: Session = Depends(get_db)):
    results = OptimizationResultRepository.get_history(db, portfolio_id)
    return [
        {
            "method": r.method,
            "weights": r.weights,
            "expected_return": r.expected_return,
            "volatility": r.volatility,
            "sharpe_ratio": r.sharpe_ratio,
            "discrete_allocation": None,
            "leftover_cash": None,
        }
        for r in results
    ]
