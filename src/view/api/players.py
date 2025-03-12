from flask import Blueprint, jsonify, request
from flask_login import login_required

from src.infra.models import Player

players_api_router = Blueprint('players_api_router', __name__)

@players_api_router.route('/api/players')
@login_required
def get_players():
    players = Player.query.with_entities(Player.name).all()
    return jsonify([{'name': p.name} for p in players])

@players_api_router.route('/api/search_players')
def search_players():
    search_term = request.args.get('term', '')
    players = Player.query.filter(Player.name.ilike(f'%{search_term}%')).limit(10).all()
    return jsonify([player.name for player in players])