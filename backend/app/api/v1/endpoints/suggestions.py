from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.suggestion import DiversificationResponse, ProfileRequest, RebalanceResponse
from app.services.suggestion_service import SuggestionService

router = APIRouter()


@router.post("/by-profile")
def suggest_by_profile(body: ProfileRequest):
    return SuggestionService.suggest_by_profile(body.risk_profile, body.capital)


@router.get("/portfolio/{portfolio_id}/diversification", response_model=DiversificationResponse)
def check_diversification(portfolio_id: int, db: Session = Depends(get_db)):
    return SuggestionService.check_diversification(db, portfolio_id)


@router.get("/portfolio/{portfolio_id}/rebalance", response_model=RebalanceResponse)
def rebalance_hints(portfolio_id: int, db: Session = Depends(get_db)):
    return SuggestionService.rebalance_hints(db, portfolio_id)
