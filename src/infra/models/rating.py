import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.database.database import Base


class RatingScope(Base):
    __tablename__ = "rating_scopes"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(256), nullable=False)
    short_name: Mapped[str] = mapped_column(sa.String(64), unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(sa.Boolean, default=True, nullable=False)
    visible: Mapped[bool] = mapped_column(sa.Boolean, default=True, nullable=False)
    games = relationship("Game", back_populates="rs")

class PlayerRating(Base):
    __tablename__ = "player_ratings"

    rs_id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    total_score: Mapped[float] = mapped_column(sa.Float, default=0.0)
    #hash?
