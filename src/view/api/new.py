import logging

from flask import request, Blueprint, jsonify, session
from flask_login import login_required

new_api_router = Blueprint('new_api_router', __name__)
logger = logging.getLogger(__name__)

@new_api_router.route('/api/update_new', methods=['POST'])
@login_required
def handle_new():
    try:
        game_data = []
        don_count = 0
        sheriff_count = 0

        result_team = request.form.get('team_victory')
        if result_team not in ['red', 'black']:
            raise ValueError("Некорректный результат игры")

        for i in range(10):
            player_name = request.form.get(f'player_{i}_name', '').strip()
            role = request.form.get(f'player_{i}_role', 'мирный').lower()
            score = float(request.form.get(f'player_{i}_score', 0))
            pu = request.form.get(f'player_{i}_pu', 'false') == 'true'
            fouls = int(request.form.get(f'player_{i}_fouls', 0))

            if player_name:
                if role in ['дон', 'мафия']:
                    team = 'black'
                else:
                    team = 'red'  # Шериф и мирные

                is_winner = (team == result_team)

                # Подсчет специальных ролей
                if role == 'дон':
                    don_count += 1
                elif role == 'шериф':
                    sheriff_count += 1

                game_data.append({
                    'player': player_name,
                    'role': role,
                    'score': score,
                    'pu': pu,
                    'fouls': fouls,
                    'is_winner': is_winner,
                    'team': team
                })

        # Валидация
        if don_count != 1:
            raise ValueError("Должен быть ровно один Дон")
        if sheriff_count != 1:
            raise ValueError("Должен быть ровно один Шериф")
        if len(game_data) < 10:
            raise ValueError("Минимум 10 игроков")

        # Сохраняем в сессию
        session['current_game'] = {
            'result': result_team,
            'pu_guess': int(request.form.get('pu_guess', 0)),
            'players': game_data
        }

        return jsonify({'status': 'success'})

    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400