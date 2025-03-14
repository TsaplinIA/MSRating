from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.infra.database import db


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    result = db.Column(db.String(10), nullable=False)
    pu_guess = db.Column(db.Integer)
    players = db.relationship('GamePlayer', backref='game', lazy=True)

class GamePlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    role = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Float, nullable=False)
    pu_active = db.Column(db.Boolean, default=False)
    player = db.relationship('Player', backref='game_players')
    is_winner = db.Column(db.Boolean, default=False)
    fouls = db.Column(db.Integer, default=0)
    elo_change = db.Column(db.Integer, default=0)

class GameModel(db.Model):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    game_datetime: Mapped[datetime] = mapped_column(db.DateTime, server_default=func.now())
    win_team: Mapped[str] = mapped_column(db.String(16), nullable=True)
    rs_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('rating_scopes.id'))

    rs = relationship("RatingScope", back_populates="games")

class GameResult(db.Model):
    __tablename__ = "game_results"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)