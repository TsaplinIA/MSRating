from sqlalchemy.orm import Mapped, mapped_column

from src.infra.database import db
from src.infra.models.games import GamePlayer


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    games = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Float, default=0.0)
    plus = db.Column(db.Float, default=0.0)
    minus = db.Column(db.Float, default=0.0)
    lh = db.Column(db.Float, default=0.0)
    wins = db.Column(db.Integer, default=0)
    wins_don = db.Column(db.Integer, default=0)
    wins_sheriff = db.Column(db.Integer, default=0)
    pu = db.Column(db.Integer, default=0)
    gg = db.Column(db.Integer, default=0)
    elo = db.Column(db.Integer, default=1000)
    winrate = db.Column(db.Float, default=0.0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_stats()

    def update_stats(self):
        self.games = GamePlayer.query.filter_by(player_id=self.id).count()
        self.wins = GamePlayer.query.filter_by(player_id=self.id, is_winner=True).count()
        try:
            self.winrate = round((self.wins / self.games) * 100, 1)
        except ZeroDivisionError:
            self.winrate = 0.0
        db.session.commit()


class PlayerModel(db.Model):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    nickname: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)
