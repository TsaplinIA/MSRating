import logging

from flask import Blueprint, render_template
from sqlalchemy.orm import aliased

from src.infra.database import db
from src.infra.models import Game, GamePlayer, Player

logger = logging.getLogger(__name__)
player_stats_router = Blueprint('player_stats', __name__)


@player_stats_router.route('/player/<int:id>')
def player_stats(id):
    try:
        player = Player.query.get(id)
        if not player:
            return render_template('404.html'), 404

        player_games = db.session.query(
            Game,
            GamePlayer.role,
            GamePlayer.score,
            GamePlayer.is_winner,
            GamePlayer.pu_active,
            GamePlayer.fouls,
            GamePlayer.elo_change
        ).join(GamePlayer, Game.id == GamePlayer.game_id)\
         .filter(GamePlayer.player_id == id)\
         .order_by(Game.date.desc())\
         .all()


        formatted_games = []
        for game, role, score, is_winner, pu_active, fouls, elo_change in player_games:
            formatted_games.append({
                "date": game.date,
                "result": "Победа" if is_winner else "Поражение",
                "role": role.capitalize(),
                "score": score,
                "pu_used": "Да" if pu_active else "Нет",
                "fouls": fouls,
                "game_result": game.result,
                "elo_change": elo_change
            })

        # Статистика по ролям
        roles = ['дон', 'шериф', 'мафия', 'мирный']
        role_stats = {role: {'games': 0, 'wins': 0, 'avg_score': 0} for role in roles}

        role_stats_query = db.session.query(
            GamePlayer.role,
            db.func.count(GamePlayer.id).label('games'),
            db.func.sum(GamePlayer.is_winner.cast(db.Integer)).label('wins'),
            db.func.avg(GamePlayer.score).label('avg_score')  # Добавляем средний балл
        ).filter_by(player_id=id).group_by(GamePlayer.role).all()

        for role, games, wins, avg_score in role_stats_query:
            role_lower = role.lower()
            if role_lower in role_stats:
                role_stats[role_lower] = {
                    'games': games or 0,
                    'wins': wins or 0,
                    'avg_score': round(avg_score, 2) if avg_score else 0
                }

        total_avg_score = db.session.query(
            db.func.avg(GamePlayer.score)
        ).filter(
            GamePlayer.player_id == id
        ).scalar()

        total_avg_score = round(total_avg_score, 2) if total_avg_score else 0

        # История ELO
        elo_changes = db.session.query(
            Game.date,
            GamePlayer.elo_change
        ).join(GamePlayer).filter(
            GamePlayer.player_id == id
        ).order_by(Game.date.asc()).all()

        elo_history = []
        current_elo = 1000
        for date, change in elo_changes:
            current_elo += change or 0
            elo_history.append({
                'date': date,
                'elo': current_elo
            })


        # Функция для поиска лучшего партнера
        def get_best_partner(team_roles):
            Partner = aliased(Player)
            try:
                result = db.session.query(
                    Partner.id,
                    Partner.name,
                    db.func.count(Game.id).label('total_games'),
                    db.func.sum(GamePlayer.is_winner.cast(db.Integer)).label('wins')
                ).join(Game, GamePlayer.game_id == Game.id)\
                 .join(Partner, GamePlayer.player_id == Partner.id)\
                 .filter(
                    GamePlayer.player_id != player.id,
                    GamePlayer.role.in_(team_roles),
                    Game.id.in_(
                        db.session.query(Game.id)
                        .join(GamePlayer)
                        .filter(
                            GamePlayer.player_id == player.id,
                            GamePlayer.role.in_(team_roles)
                        )
                    )
                 )\
                 .group_by(Partner.id)\
                 .order_by(db.desc('wins'), db.desc('total_games'))\
                 .first()
                return result if result else None
            except Exception as e:
                logger.error(f"Partner query error: {str(e)}")
                return None

        # Поиск лучших партнеров
        best_partners = {'black': None, 'red': None}

        black_data = get_best_partner(['дон', 'мафия'])
        if black_data:
            best_partners['black'] = {
                'id': black_data[0],
                'name': black_data[1],
                'games': black_data[2] or 0,
                'wins': black_data[3] or 0,
                'winrate': round((black_data[3] / black_data[2] * 100), 1) if black_data[2] > 0 else 0
            }

        red_data = get_best_partner(['шериф', 'мирный'])
        if red_data:
            best_partners['red'] = {
                'id': red_data[0],
                'name': red_data[1],
                'games': red_data[2] or 0,
                'wins': red_data[3] or 0,
                'winrate': round((red_data[3] / red_data[2] * 100), 1) if red_data[2] > 0 else 0
            }

        return render_template(
            'player.html',
            player=player,
            games_history=formatted_games,
            stats={
                'roles': role_stats,
                'total_games': sum(r['games'] for r in role_stats.values()),
                'total_wins': sum(r['wins'] for r in role_stats.values()),
                'total_avg_score': total_avg_score
            },
            best_partners=best_partners
        )

    except Exception as e:
        logger.error(f"Error in player_stats: {str(e)}", exc_info=True)
        return render_template('500.html'), 500
