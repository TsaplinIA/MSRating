from flask import Blueprint, render_template

from src.infra.database import db
from src.infra.models import Game, GamePlayer, Player

games_router = Blueprint('games', __name__)

@games_router.route('/saved_games')
def show_saved_games():
    games = Game.query.order_by(Game.date.desc()).all()

    game_players = {
        game.id: db.session.query(GamePlayer, Player.name)
        .join(Player, GamePlayer.player_id == Player.id)
        .filter(GamePlayer.game_id == game.id)
        .all()
        for game in games
    }

    return render_template('saved_games.html', games=games, game_players=game_players)