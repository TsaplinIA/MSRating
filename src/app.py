import pytz
from flask import Flask

from src import config
from src.infra.database import db
from src.view import (
    admin_router,
    games_router,
    home_router,
    login_router,
    new_api_router,
    new_router,
    player_stats_router,
    players_api_router,
    rating_api_router,
    rating_router,
)
from src.view.pages.login import login_manager


def format_datetime(value):
    moscow_tz = pytz.timezone('Europe/Moscow')
    if value.tzinfo is None:
        value = pytz.utc.localize(value)
    localized = value.astimezone(moscow_tz)
    return localized.strftime('%d.%m.%Y')

def build_flask_app():
    flask_app = Flask('MSRating')
    flask_app.config['SECRET_KEY'] = config.APP_SECRET_KEY
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.template_folder = config.TEMPLATE_DIR.resolve()
    flask_app.static_folder = config.STATIC_DIR.resolve()
    flask_app.template_filter('datetime')(format_datetime)

    db.init_app(flask_app)
    login_manager.init_app(flask_app)

    blueprints = [
        new_api_router,
        players_api_router,
        rating_api_router,
        admin_router,
        games_router,
        home_router,
        login_router,
        new_router,
        player_stats_router,
        rating_router,
    ]
    for bp in blueprints:
        flask_app.register_blueprint(bp)

    with flask_app.app_context():
        db.create_all()

    return flask_app


def run_app(flask_app):
    flask_app.run(debug=True, port=config.PORT, host=config.HOST)

app = build_flask_app()

if __name__ == '__main__':
    run_app(app)
