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


def build_flask_app():
    flask_app = Flask('MSRating')
    flask_app.config['SECRET_KEY'] = config.APP_SECRET_KEY
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(flask_app)
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

    return flask_app


def run_app(flask_app):
    with app.app_context():
        db.create_all()
    flask_app.run(debug=True)

app = build_flask_app()

if __name__ == '__main__':
    run_app(app)
