import logging
from datetime import datetime

import pytz
from flask import Blueprint, jsonify, session, url_for
from flask_login import login_required

from src.infra.database import db
from src.infra.models import Game, GamePlayer, Player

rating_api_router = Blueprint('rating_api_router', __name__)
logger = logging.getLogger(__name__)

@rating_api_router.route('/api/update_rating', methods=['POST'])
@login_required
def handle_rating():
    try:
        game_info = session.get('current_game')
        if not game_info:
            raise ValueError("Данные игры не найдены в сессии")

        new_game = Game(
            result=game_info['result'],
            pu_guess=game_info['pu_guess'],
            date=datetime.now(pytz.timezone('Europe/Moscow'))  # <--- Закрывающая скобка
        )  # <--- Здесь!
        db.session.add(new_game)
        db.session.flush()

        players_data = []
        black_team = []
        red_team = []

        for player_data in game_info['players']:
            player = db.session.query(Player).filter_by(name=player_data['player']).first()
            if not player:
                player = Player(name=player_data['player'])
                db.session.add(player)
                db.session.flush()

            game_player = GamePlayer(
                game_id=new_game.id,
                player_id=player.id,
                role=player_data['role'],
                score=player_data['score'],
                pu_active=player_data['pu'],
                is_winner=player_data['is_winner'],
                fouls=player_data['fouls'],
                elo_change=0
            )
            db.session.add(game_player)

            player.games += 1
            player.total_score += player_data['score']

            if player_data['is_winner']:
                player.wins += 1
                if player_data['role'] == 'дон':
                    player.wins_don += 1
                elif player_data['role'] == 'шериф':
                    player.wins_sheriff += 1

            # Распределяем по командам для ELO
            if player_data['role'] in ['дон', 'мафия']:
                black_team.append(player)
            else:
                red_team.append(player)

            players_data.append({
                'player': player,
                'game_player': game_player,
                'team': 'black' if player_data['role'] in ['дон', 'мафия'] else 'red',
                'score': player_data['score'],
                'is_winner': player_data['is_winner'],
                'role': player_data['role']
            })

        avg_black = sum(p.elo for p in black_team) / len(black_team) if black_team else 1000
        avg_red = sum(p.elo for p in red_team) / len(red_team) if red_team else 1000

        for data in players_data:
            player = data['player']
            game_player = data['game_player']
            actual_result = 1 if data['is_winner'] else 0

            if data['team'] == 'black':
                expected_result = 1 / (1 + 10**((avg_red - avg_black)/400))
            else:
                expected_result = 1 / (1 + 10**((avg_black - avg_red)/400))

            role_mod = 1.3 if data['role'] in ['дон', 'шериф'] else 1.0 if data['role'] == 'мафия' else 1.1
            score_mod = data['score']
            A = 45
            if (game_player.pu_active and new_game.pu_guess > 1 and actual_result == 0) or (score_mod >= 0.1 and actual_result == 0):
                s = 0
            else:
                s = 32

            delta = s * (actual_result - expected_result) * role_mod + (A * score_mod)
            game_player.elo_change = delta
            player.elo = max(150, player.elo + int(delta))

            player.update_stats()

        # Фиксируем все изменения
        db.session.commit()

        session.pop('current_game', None)
        return jsonify({'status': 'success', 'redirect': url_for('show_rating')})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка сохранения: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Ошибка сохранения игры: {str(e)}'}), 500
