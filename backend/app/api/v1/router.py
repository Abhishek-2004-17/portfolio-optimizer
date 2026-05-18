from fastapi import APIRouter

from app.api.v1.endpoints import data, optimization, portfolios, risk, suggestions, tickers

api_router = APIRouter()

api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(optimization.router, prefix="/optimization", tags=["optimization"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(suggestions.router, prefix="/suggestions", tags=["suggestions"])
api_router.include_router(tickers.router, prefix="/tickers", tags=["tickers"])
