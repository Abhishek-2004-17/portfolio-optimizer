from pydantic import BaseModel


class TickerItem(BaseModel):
    """A single ticker result."""

    symbol: str
    name: str


class TickerSearchResponse(BaseModel):
    """Response for ticker search."""

    results: list[TickerItem]


class TickerValidateResponse(BaseModel):
    """Response for ticker validation."""

    symbol: str
    name: str | None = None
    valid: bool = True
