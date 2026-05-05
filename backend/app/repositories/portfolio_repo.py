from sqlalchemy.orm import Session, selectinload

from app.models.portfolio import Portfolio
from app.models.portfolio_asset import PortfolioAsset
from app.repositories.base import BaseRepository
from app.schemas.portfolio import (
    PortfolioAssetCreate,
    PortfolioAssetUpdate,
    PortfolioCreate,
    PortfolioUpdate,
)


class PortfolioRepository(
    BaseRepository[Portfolio, PortfolioCreate, PortfolioUpdate]
):
    def get_with_assets(self, db: Session, portfolio_id: int) -> Portfolio | None:
        return (
            db.query(self.model)
            .options(selectinload(self.model.assets))
            .filter(self.model.id == portfolio_id)
            .first()
        )

    def list_with_assets(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[Portfolio]:
        return (
            db.query(self.model)
            .options(selectinload(self.model.assets))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def add_asset(
        self, db: Session, portfolio_id: int, *, obj_in: PortfolioAssetCreate
    ) -> PortfolioAsset:
        asset_data = obj_in.model_dump()
        asset_data["portfolio_id"] = portfolio_id
        db_asset = PortfolioAsset(**asset_data)
        db.add(db_asset)
        db.flush()
        db.refresh(db_asset)
        return db_asset

    def update_asset(
        self,
        db: Session,
        asset: PortfolioAsset,
        *,
        obj_in: PortfolioAssetUpdate,
    ) -> PortfolioAsset:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(asset, field, value)
        db.add(asset)
        db.flush()
        db.refresh(asset)
        return asset

    def remove_asset(self, db: Session, *, asset: PortfolioAsset) -> PortfolioAsset:
        db.delete(asset)
        db.flush()
        return asset


portfolio_repo = PortfolioRepository(Portfolio)
