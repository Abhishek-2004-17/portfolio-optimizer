from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.models.portfolio_asset import PortfolioAsset
from app.repositories.portfolio_repo import portfolio_repo
from app.schemas.portfolio import (
    PortfolioAssetCreate,
    PortfolioAssetResponse,
    PortfolioAssetUpdate,
    PortfolioCreate,
    PortfolioResponse,
    PortfolioUpdate,
)

router = APIRouter()


@router.post("", response_model=PortfolioResponse, status_code=201)
def create_portfolio(body: PortfolioCreate, db: Session = Depends(get_db)):
    portfolio = portfolio_repo.create(db, obj_in=body)
    db.commit()
    return portfolio_repo.get_with_assets(db, portfolio.id)


@router.get("", response_model=list[PortfolioResponse])
def list_portfolios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return portfolio_repo.list_with_assets(db, skip=skip, limit=limit)


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = portfolio_repo.get_with_assets(db, portfolio_id)
    if portfolio is None:
        raise NotFoundError(detail=f"Portfolio {portfolio_id} not found")
    return portfolio


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(
    portfolio_id: int, body: PortfolioUpdate, db: Session = Depends(get_db)
):
    portfolio = portfolio_repo.get(db, portfolio_id)
    if portfolio is None:
        raise NotFoundError(detail=f"Portfolio {portfolio_id} not found")
    portfolio_repo.update(db, db_obj=portfolio, obj_in=body)
    db.commit()
    return portfolio_repo.get_with_assets(db, portfolio_id)


@router.delete("/{portfolio_id}", status_code=204)
def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = portfolio_repo.get(db, portfolio_id)
    if portfolio is None:
        raise NotFoundError(detail=f"Portfolio {portfolio_id} not found")
    portfolio_repo.delete(db, id=portfolio_id)
    db.commit()


@router.get("/{portfolio_id}/assets", response_model=list[PortfolioAssetResponse])
def list_assets(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = portfolio_repo.get(db, portfolio_id)
    if portfolio is None:
        raise NotFoundError(detail=f"Portfolio {portfolio_id} not found")
    # Refresh to load assets relationship
    db.refresh(portfolio, ["assets"])
    return portfolio.assets


@router.post(
    "/{portfolio_id}/assets", response_model=PortfolioAssetResponse, status_code=201
)
def add_asset(
    portfolio_id: int, body: PortfolioAssetCreate, db: Session = Depends(get_db)
):
    portfolio = portfolio_repo.get(db, portfolio_id)
    if portfolio is None:
        raise NotFoundError(detail=f"Portfolio {portfolio_id} not found")

    # Check unique constraint: same ticker cannot be added twice
    existing = (
        db.query(PortfolioAsset)
        .filter(
            PortfolioAsset.portfolio_id == portfolio_id,
            PortfolioAsset.ticker == body.ticker,
        )
        .first()
    )
    if existing is not None:
        raise ValidationError(
            detail=f"Asset with ticker '{body.ticker}' already exists in portfolio {portfolio_id}"
        )

    asset = portfolio_repo.add_asset(db, portfolio_id, obj_in=body)
    db.commit()
    return asset


@router.put(
    "/{portfolio_id}/assets/{asset_id}", response_model=PortfolioAssetResponse
)
def update_asset(
    portfolio_id: int,
    asset_id: int,
    body: PortfolioAssetUpdate,
    db: Session = Depends(get_db),
):
    portfolio = portfolio_repo.get(db, portfolio_id)
    if portfolio is None:
        raise NotFoundError(detail=f"Portfolio {portfolio_id} not found")

    asset = db.get(PortfolioAsset, asset_id)
    if asset is None or asset.portfolio_id != portfolio_id:
        raise NotFoundError(
            detail=f"Asset {asset_id} not found in portfolio {portfolio_id}"
        )

    portfolio_repo.update_asset(db, asset, obj_in=body)
    db.commit()
    return asset


@router.delete("/{portfolio_id}/assets/{asset_id}", status_code=204)
def delete_asset(
    portfolio_id: int, asset_id: int, db: Session = Depends(get_db)
):
    portfolio = portfolio_repo.get(db, portfolio_id)
    if portfolio is None:
        raise NotFoundError(detail=f"Portfolio {portfolio_id} not found")

    asset = db.get(PortfolioAsset, asset_id)
    if asset is None or asset.portfolio_id != portfolio_id:
        raise NotFoundError(
            detail=f"Asset {asset_id} not found in portfolio {portfolio_id}"
        )

    portfolio_repo.remove_asset(db, asset=asset)
    db.commit()
