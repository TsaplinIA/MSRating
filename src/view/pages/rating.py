import logging
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request
from sqlalchemy import and_, case

from src import config
from src.infra.database import db
from src.infra.models import Game, GamePlayer, Player

rating_router = Blueprint('rating_router', __name__)
logger = logging.getLogger(__name__)

@rating_router.route('/rating')
def show_rating():
    try:
        selected_period = request.args.get('period', 'all')
        start_date, end_date = None, None

        from dateutil.relativedelta import relativedelta

        if selected_period != 'all':
            year_str, period_num = selected_period.split('-')
            year = int(year_str)
            period_num = int(period_num)

            start_month = (period_num - 1) * 2 + 1
            end_month = start_month + 1
            end_year = year

            if end_month > 12:
                end_month = 1
                end_year = year + 1

            start_date = datetime(year, start_month, 1)
            end_date = datetime(end_year, end_month, 1) + relativedelta(months=1) - timedelta(seconds=1)


        # Базовый запрос
        query = db.session.query(
            GamePlayer.player_id,
            Player,
            db.func.count(GamePlayer.id).label('total_games'),
            db.func.sum(
                GamePlayer.score +
                case(
                    [
                        (and_(GamePlayer.pu_active, Game.pu_guess == 3), 0.5),
                        (and_(GamePlayer.pu_active, Game.pu_guess == 2), 0.25)
                    ],
                    else_=0.0
                )
            ).label('total_score'),
            db.func.sum(
                case((GamePlayer.is_winner, 1), else_=0)
            ).label('total_wins'),
            db.func.sum(
                case((GamePlayer.score > 0, GamePlayer.score), else_=0)
            ).label('positive'),
            db.func.sum(
                case((GamePlayer.score < 0, db.func.abs(GamePlayer.score)), else_=0)
            ).label('negative'),
            db.func.sum(
                case((GamePlayer.pu_active, 1), else_=0)
            ).label('pu_count'),
            db.func.sum(
                case(
                    (and_(GamePlayer.role == 'дон', GamePlayer.is_winner), 1),
                    else_=0
                )
            ).label('don_wins'),
            db.func.sum(
                case(
                    (and_(GamePlayer.role == 'шериф', GamePlayer.is_winner), 1),
                    else_=0
                )
            ).label('sheriff_wins'),
            db.func.sum(
                case(
                    [
                        (and_(GamePlayer.pu_active, Game.pu_guess == 3), 0.5),
                        (and_(GamePlayer.pu_active, Game.pu_guess == 2), 0.25)
                    ],
                    else_=0.0
                )
            ).label('lh_points'),
            db.func.sum(
                case((GamePlayer.role == 'мирный', 1), else_=0)
            ).label('civilian_games')
        ).select_from(GamePlayer) \
        .join(Game, GamePlayer.game_id == Game.id) \
        .join(Player, GamePlayer.player_id == Player.id)

        if start_date and end_date:
            query = query.filter(Game.date.between(start_date, end_date))

        results = query.group_by(GamePlayer.player_id).all()


        table_data = []
        for res in results:
            player = res[1]

            total_games = int(res[2]) if res[2] else 0
            total_wins = int(res[4]) if res[4] else 0
            total_score = (float(res[3]) + total_wins) if res[3] else (0.0 + total_wins)
            pu_count = float(res[7]) if res[7] else 0.0  # Decimal -> Float
            gg_value = float(player.gg) if player.gg else 0.0  # Int -> Float


            try:
                win_rate = total_wins / total_games
            except ZeroDivisionError:
                win_rate = 0.0

            r_score = (
                total_score * win_rate
                + (pu_count * 0.1)
                + (gg_value * 0.2)
            )

            table_data.append({
                'id': player.id,
                'Игрок': player.name,
                'ELO': player.elo,
                'GG': int(gg_value),
                'Игры': total_games,
                'Σ': round(total_score, 2),
                'Winrate': round(win_rate * 100, 1),
                '+': round(float(res[5] or 0.0), 2),
                '-': round(float(res[6] or 0.0), 2),
                'ЛХ': round(float(res[10] or 0.0), 2),
                'Побед': total_wins,
                'Доном': int(res[8] or 0),
                'Шерифом': int(res[9] or 0),
                'ПУ': int(pu_count),
                'Рейтинговый балл': round(r_score, 2)
            })

        sorted_data = sorted(
            table_data,
            key=lambda x: x['Рейтинговый балл'],
            reverse=True
        )
        for idx, item in enumerate(sorted_data):
            item['№'] = idx + 1

        return render_template(
            'rating.html',
            table=table_data,
            periods=config.FIXED_PERIODS,
            selected_period=selected_period
        )

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return render_template('error.html'), 500
