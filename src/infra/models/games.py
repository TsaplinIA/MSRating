from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import func, UniqueConstraint, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.database.database import Base
from src.infra.enums import Role, Team


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    game_datetime: Mapped[datetime] = mapped_column(sa.DateTime, server_default=func.now())
    win_team: Mapped[str] = mapped_column(sa.Enum(Team), nullable=True)
    judge_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey('players.id'), nullable=True)
    description: Mapped[str] = mapped_column(sa.Text, nullable=True)
    rs_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey('rating_scopes.id'), nullable=False)
    tour_number: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    extra_info: Mapped[dict] = mapped_column(sa.JSON, nullable=True)

    # Отношения
    rs = relationship("RatingScope", back_populates="games")
    judge = relationship("Player")

    # Ограничение на уникальность тура внутри рейтинг-скоупа
    __table_args__ = (
        UniqueConstraint('rs_id', 'tour_number', name='uix_rs_tour'),
    )


class GameResult(Base):
    __tablename__ = "game_results"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey('games.id'), nullable=False)
    player_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey('players.id'), nullable=False)
    player_number: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    player_role: Mapped[str] = mapped_column(sa.Enum(Role), nullable=True)
    player_team: Mapped[str] = mapped_column(sa.Enum(Team), nullable=True)
    dop_ball_plus: Mapped[float] = mapped_column(sa.Float, default=0.0)
    dop_ball_minus: Mapped[float] = mapped_column(sa.Float, default=0.0)
    is_first_blood: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    lh: Mapped[list[int]] = mapped_column(ARRAY(sa.SmallInteger, dimensions=1), nullable=True)
    is_kicked: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    is_ppk_initiator: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    is_has_compensation: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    extra_info: Mapped[dict] = mapped_column(sa.JSON, nullable=True)

    # Компенс, победа Итоговый балл,

    # Отношения
    game = relationship("Game")
    player = relationship("Player")
