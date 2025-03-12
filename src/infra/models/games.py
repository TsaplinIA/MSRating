from datetime import datetime

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