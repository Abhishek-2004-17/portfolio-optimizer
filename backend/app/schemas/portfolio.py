from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PortfolioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    base_currency: str = "USD"
    initial_capital: float = Field(..., gt=0)


class PortfolioUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None


class PortfolioAssetCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)
    weight: float | None = Field(None, ge=0, le=1)
    shares: float | None = Field(None, ge=0)
    purchase_price: float | None = Field(None, gt=0)


class PortfolioAssetUpdate(BaseModel):
    weight: float | None = Field(None, ge=0, le=1)
    shares: float | None = Field(None, ge=0)


class PortfolioAssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    weight: float | None
    shares: float | None
    purchase_price: float | None
    added_at: datetime


class PortfolioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    base_currency: str
    initial_capital: float
    created_at: datetime
    updated_at: datetime
    assets: list[PortfolioAssetResponse] = []
