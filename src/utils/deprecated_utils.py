import logging
from datetime import datetime

import pytz
from sqlalchemy import and_, case

from src import config
from src.infra.models import Game, GamePlayer, Player
from src.infra.database import db


logger = logging.getLogger(__name__)

def get_current_season():
    now = datetime.now(pytz.timezone('Europe/Moscow'))
    current_date = now.date()

    for season in config.SEASONS:
        start = datetime.strptime(config.SEASONS[season][0], '%Y-%m-%d').date()
        end = datetime.strptime(config.SEASONS[season][1], '%Y-%m-%d').date()
        if start <= current_date <= end:
            return season
    return '2025-1'

def parse_season(season_str):
    if season_str == 'all':
        return None, None

    dates = config.SEASONS.get(season_str, ('2000-01-01', '2100-01-01'))
    start = datetime.strptime(dates[0], '%Y-%m-%d').replace(tzinfo=pytz.UTC)
    end = datetime.strptime(dates[1], '%Y-%m-%d').replace(
        hour=23, minute=59, second=59, tzinfo=pytz.UTC)

    return start, end

def get_top_players(start_date=None, end_date=None, limit=10):
    try:
        session = db.session
        with session.begin():
            lh_case = case(
                [
                    (and_(GamePlayer.pu_active == 1, Game.pu_guess == 3), 0.5),
                    (and_(GamePlayer.pu_active == 1, Game.pu_guess == 2), 0.25)
                ],
                else_=0.0
            )

            pu_count_case = case(
                [(GamePlayer.pu_active == 1, 1)],
                else_=0
            )

            query = session.query(
                Player.id,
                Player.name,
                db.func.coalesce(
                    db.func.sum(GamePlayer.score)
                    + db.func.sum(GamePlayer.is_winner)
                    + db.func.sum(lh_case),
                    0.0
                ).label('total_score'),

                db.func.round(
                    db.func.coalesce(db.func.avg(GamePlayer.is_winner) * 100, 0.0
                ), 1
                ).label('winrate'),

                # R-Score: (total_score * winrate) + (pu_count * 0.1) + (gg * 0.2)
                (
                    (
                        (
                            db.func.coalesce(db.func.sum(GamePlayer.score), 0.0)
                            + db.func.coalesce(db.func.sum(GamePlayer.is_winner), 0.0)
                            + db.func.coalesce(db.func.sum(lh_case), 0.0)
                        )
                        * db.func.coalesce(db.func.avg(GamePlayer.is_winner), 0.0)
                    )
                    + (db.func.coalesce(db.func.sum(pu_count_case), 0.0) * 0.1)
                    + (db.func.coalesce(Player.gg, 0.0) * 0.2)
                ).label('r_score'),

                Player.elo
            ).join(GamePlayer, Player.id == GamePlayer.player_id) \
             .join(Game, Game.id == GamePlayer.game_id)

            if start_date and end_date:
                query = query.filter(Game.date.between(start_date, end_date))

            result = query.group_by(Player.id) \
                        .order_by(db.desc('r_score')) \
                        .limit(limit).all()

            return result

    except Exception as e:
        session.rollback()
        logger.error(f"Error in get_top_players: {str(e)}")
        return []

    except Exception as e:
        session.rollback()
        logger.error(f"Error in get_top_players: {str(e)}")
        return []

def calculate_role_stats(season):
    roles = ['дон', 'шериф', 'мафия', 'мирный']
    stats = {}

    try:
        from sqlalchemy.orm import scoped_session, sessionmaker
        session = scoped_session(sessionmaker(bind=db.engine))

        for role in roles:
            try:
                with session.begin():
                    subquery = session.query(
                        GamePlayer.player_id,
                        db.func.sum(GamePlayer.score).label('total_score')
                    ).join(Game).filter(GamePlayer.role == role)

                    if season != 'all':
                        start, end = parse_season(season)
                        subquery = subquery.filter(Game.date.between(start, end))

                    subquery = subquery.group_by(GamePlayer.player_id).subquery()

                    best_player = session.query(
                        Player.id,
                        Player.name,
                        db.func.coalesce(subquery.c.total_score, 0.0).label('score')
                    ).outerjoin(subquery, Player.id == subquery.c.player_id
                    ).order_by(db.desc('score')).first()

                    stats[role] = {
                        'name': best_player.name if best_player else 'Нет данных',
                        'score': round(best_player.score, 2) if best_player else 0.0
                    }

            except Exception as e:
                session.rollback()
                logger.error(f"Error processing {role}: {str(e)}")
                stats[role] = {'name': 'Ошибка', 'score': 0.0}

        try:
            with session.begin():
                subquery = session.query(
                    GamePlayer.player_id,
                    db.func.sum(GamePlayer.score).label('total_score')
                ).join(Game)

                if season != 'all':
                    start, end = parse_season(season)
                    subquery = subquery.filter(Game.date.between(start, end))

                subquery = subquery.group_by(GamePlayer.player_id).subquery()

                mvp_player = session.query(
                    Player.id,
                    Player.name,
                    db.func.coalesce(subquery.c.total_score, 0.0).label('score')
                ).outerjoin(subquery, Player.id == subquery.c.player_id
                ).order_by(db.desc('score')).first()

                mvp = {
                    'name': mvp_player.name if mvp_player else 'Нет данных',
                    'score': round(mvp_player.score, 2) if mvp_player else 0.0
                }

        except Exception as e:
            session.rollback()
            logger.error(f"Error processing MVP: {str(e)}")
            mvp = {'name': 'Ошибка', 'score': 0.0}

        return stats, mvp

    finally:
        session.remove()
