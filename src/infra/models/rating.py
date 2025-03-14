from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.database import db


class RatingScope(db.Model):
    __tablename__ = "rating_scopes"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(256), nullable=False)
    short_name: Mapped[str] = mapped_column(db.String(64), unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)

    games = relationship("GameModel", back_populates="rs")

class PlayerRating(db.Model):
    __tablename__ = "player_ratings"

    rs_id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    total_score = db.Column(db.Float, default=0.0)
    #hash?