from pydantic import BaseModel, Field


class ProfileRequest(BaseModel):
    risk_profile: str = Field(..., pattern="^(conservative|moderate|aggressive)$")
    capital: float = Field(..., gt=0)


class SuggestionResponse(BaseModel):
    severity: str
    message: str
    detail: str | None = None


class DiversificationResponse(BaseModel):
    herfindahl_index: float
    max_weight: float
    max_weight_ticker: str
    suggestions: list[SuggestionResponse]


class RebalanceResponse(BaseModel):
    drift_items: list[dict[str, float]]
    needs_rebalance: bool
    suggestions: list[SuggestionResponse]
