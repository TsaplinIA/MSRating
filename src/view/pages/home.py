from flask import Blueprint, render_template

from src import config
from src.utils.deprecated_utils import (
    calculate_role_stats,
    get_current_season,
    get_top_players,
    parse_season,
)

home_router = Blueprint('home_router', __name__)

@home_router.route('/')
def home():
    current_season = get_current_season()
    start_date, end_date = parse_season(current_season)

    all_time_stats, all_time_mvp = calculate_role_stats('all')
    season_stats, season_mvp = calculate_role_stats(current_season)

    season_players = get_top_players(start_date, end_date, limit=10)

    return render_template(
        'index.html',
        top_players=season_players,
        all_time_stats=all_time_stats,
        season_stats=season_stats,
        current_season=next((p['name'] for p in config.FIXED_PERIODS if p['value'] == current_season), 'Текущий сезон'),
        all_time_mvp=all_time_mvp,
        season_mvp=season_mvp
    )
