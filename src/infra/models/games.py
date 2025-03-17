from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.database.database import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    game_datetime: Mapped[datetime] = mapped_column(sa.DateTime, server_default=func.now())
    win_team: Mapped[str] = mapped_column(sa.String(16), nullable=True)
    rs_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey('rating_scopes.id'), nullable=False)

    rs = relationship("RatingScope", back_populates="games", foreign_keys=[rs_id])

class GameResult(Base):
    __tablename__ = "game_results"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
