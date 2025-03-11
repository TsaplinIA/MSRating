from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import logging
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
from urllib.parse import unquote
import pytz
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy import extract, and_, or_, case, asc, desc, not_, func
from flask import session as flask_session
from sqlalchemy.orm import aliased


logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.config['SECRET_KEY'] = '3e9b8e07d7b3f2a1c4d6f5907b8a2d3c1e5f7a9b0d2c4e6f8a1b3d5e7f9a0b2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://MafiaStyle:bauRm8VuDseE6MQ@MafiaStyle.mysql.pythonanywhere-services.com/MafiaStyle$default'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ADMIN_SECRET_CODE = 'ms4ever'

SEASONS = {
    '2025-1': ('2025-01-01', '2025-02-28'),
    '2025-2': ('2025-03-01', '2025-04-30'),
    '2025-3': ('2025-05-01', '2025-06-30'),
    '2025-4': ('2025-07-01', '2025-08-31'),
    '2025-5': ('2025-09-01', '2025-10-31'),
    '2025-6': ('2025-11-01', '2025-12-31')
}

ROLES_MAP = {
    'дон': 'black',
    'мафия': 'black',
    'шериф': 'red',
    'мирный': 'red'
}

TEAM_ROLES = {
    'дон': {'дон': 1, 'мафия': 2},
    'мафия': {'дон': 1, 'мафия': 2},
    'шериф': {'шериф': 1, 'мирный': 6},
    'мирный': {'шериф': 1, 'мирный': 6}
}

OPPONENT_ROLES = {
    'дон': {'шериф': 1, 'мирный': 6},
    'мафия': {'шериф': 1, 'мирный': 6},
    'шериф': {'дон': 1, 'мафия': 2},
    'мирный': {'дон': 1, 'мафия': 2}
}

FIXED_PERIODS = [
    {'value': 'all', 'name': 'Все время'},
    {'value': '2025-1', 'name': 'Январь-Февраль 2025'},
    {'value': '2025-2', 'name': 'Март-Апрель 2025'},
    {'value': '2025-3', 'name': 'Май-Июнь 2025'},
    {'value': '2025-4', 'name': 'Июль-Август 2025'},
    {'value': '2025-5', 'name': 'Сентябрь-Октябрь 2025'},
    {'value': '2025-6', 'name': 'Ноябрь-Декабрь 2025'}
]

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
#DB Models edited
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    games = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Float, default=0.0)
    plus = db.Column(db.Float, default=0.0)
    minus = db.Column(db.Float, default=0.0)
    lh = db.Column(db.Float, default=0.0)
    wins = db.Column(db.Integer, default=0)
    wins_don = db.Column(db.Integer, default=0)
    wins_sheriff = db.Column(db.Integer, default=0)
    pu = db.Column(db.Integer, default=0)
    gg = db.Column(db.Integer, default=0)
    elo = db.Column(db.Integer, default=1000)
    winrate = db.Column(db.Float, default=0.0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_stats()

    def update_stats(self):
        self.games = GamePlayer.query.filter_by(player_id=self.id).count()
        self.wins = GamePlayer.query.filter_by(player_id=self.id, is_winner=True).count()
        try:
            self.winrate = round((self.wins / self.games) * 100, 1)
        except ZeroDivisionError:
            self.winrate = 0.0
        db.session.commit()


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    result = db.Column(db.String(10), nullable=False)
    pu_guess = db.Column(db.Integer)
    players = db.relationship('GamePlayer', backref='game', lazy=True)

class GamePlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    role = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Float, nullable=False)
    pu_active = db.Column(db.Boolean, default=False)
    player = db.relationship('Player', backref='game_players')
    is_winner = db.Column(db.Boolean, default=False)
    fouls = db.Column(db.Integer, default=0)
    elo_change = db.Column(db.Integer, default=0)

#Auth routes (test need!)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("Получены данные:", request.form)  # ← Отладка
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        print("Найден пользователь:", user)  # ← Отладка

        if user:
            print("Проверка пароля:", (user.password == password))  # ← Отладка

        if user and (user.password == password):
            login_user(user)
            print("Успешный вход!")  # ← Отладка
            return redirect(url_for('home'))

        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin_code = request.form.get('admin_code', '').strip()

        is_admin = (admin_code == ADMIN_SECRET_CODE)

        if not username or not password:
            flash("Заполните все обязательные поля", "error")
            return redirect(url_for('register'))

        new_user = User(
            username=username,
            password=password,
            is_admin=is_admin
        )

        db.session.add(new_user)
        db.session.commit()
        flash("Регистрация успешно завершена!", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

#functions
def get_current_season():
    now = datetime.now(pytz.timezone('Europe/Moscow'))
    current_date = now.date()

    for season in SEASONS:
        start = datetime.strptime(SEASONS[season][0], '%Y-%m-%d').date()
        end = datetime.strptime(SEASONS[season][1], '%Y-%m-%d').date()
        if start <= current_date <= end:
            return season
    return '2025-1' 

def parse_season(season_str):
    if season_str == 'all':
        return None, None

    dates = SEASONS.get(season_str, ('2000-01-01', '2100-01-01'))
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
        app.logger.error(f"Error in get_top_players: {str(e)}")
        return []

    except Exception as e:
        session.rollback()
        app.logger.error(f"Error in get_top_players: {str(e)}")
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
                app.logger.error(f"Error processing {role}: {str(e)}")
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
            app.logger.error(f"Error processing MVP: {str(e)}")
            mvp = {'name': 'Ошибка', 'score': 0.0}

        return stats, mvp

    finally:
        session.remove()

#Brainfucking part
@app.route('/admin/add_gg', methods=['GET', 'POST'])
@login_required
def admin_add_gg():
    if not current_user.is_admin:
        return render_template('403.html'), 403

    if request.method == 'POST':
        if 'confirm_create' in request.form:
            player_name = request.form.get('player_name')
            gg_value = request.form.get('gg_value')

            try:
                gg_value = int(gg_value)

                new_player = Player(
                    name=player_name,
                    gg=gg_value
                )

                db.session.add(new_player)
                db.session.commit()
                flash('Новый игрок успешно создан', 'success')
                return redirect(url_for('admin_add_gg'))

            except ValueError:
                flash('Некорректное значение GG', 'danger')
            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка при создании игрока: {str(e)}', 'danger')

            return render_template('admin_add_gg.html',
                                 show_confirmation=True,
                                 player_name=player_name,
                                 gg_value=gg_value)

        player_name = request.form.get('player_name')
        gg_value = request.form.get('gg_value')

        try:
            gg_value = int(gg_value)
            player = Player.query.filter_by(name=player_name).first()

            if not player:
                return render_template('admin_add_gg.html',
                                     show_confirmation=True,
                                     player_name=player_name,
                                     gg_value=gg_value)
            else:
                player.gg = gg_value
                db.session.commit()
                flash('GG значение успешно обновлено', 'success')

        except ValueError:
            flash('Некорректное значение GG', 'danger')

    return render_template('admin_add_gg.html', show_confirmation=False)

@app.route('/')
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
        current_season=next((p['name'] for p in FIXED_PERIODS if p['value'] == current_season), 'Текущий сезон'),
        all_time_mvp=all_time_mvp,
        season_mvp=season_mvp
    )

@app.route('/rating')
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
            db.func.sum(case((GamePlayer.is_winner, 1), else_=0)).label('total_wins'),
            db.func.sum(case((GamePlayer.score > 0, GamePlayer.score), else_=0)).label('positive'),
            db.func.sum(case((GamePlayer.score < 0, db.func.abs(GamePlayer.score)), else_=0)).label('negative'),
            db.func.sum(case((GamePlayer.pu_active, 1), else_=0)).label('pu_count'),
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
            db.func.sum(case((GamePlayer.role == 'мирный', 1), else_=0)).label('civilian_games')
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

        sorted_data = sorted(table_data, key=lambda x: x['Рейтинговый балл'], reverse=True)
        for idx, item in enumerate(sorted_data):
            item['№'] = idx + 1

        return render_template(
            'rating.html',
            table=table_data,
            periods=FIXED_PERIODS,
            selected_period=selected_period
        )

    except Exception as e:
        app.logger.error(f"Ошибка: {str(e)}")
        return render_template('error.html'), 500

@app.route('/new')
@login_required
def show_new():
    if not current_user.is_admin:
        return render_template('403.html'), 403

    default_table = [{
        '№': i+1,
        'Игрок': '',
        'Балл': 0.0,
        'Роль': 'Мирный',
        'Фолы': 0,
        'ПУ': False
    } for i in range(10)]

    table_data = session.get('current_game', default_table)
    return render_template('new.html', table=table_data)

@app.route('/api/update_new', methods=['POST'])
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
        flask_session['current_game'] = {
            'result': result_team,
            'pu_guess': int(request.form.get('pu_guess', 0)),
            'players': game_data
        }

        return jsonify({'status': 'success'})

    except Exception as e:
        app.logger.error(f"Validation error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/update_rating', methods=['POST'])
@login_required
def handle_rating():
    try:
        game_info = flask_session.get('current_game')
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

        flask_session.pop('current_game', None)
        return jsonify({'status': 'success', 'redirect': url_for('show_rating')})

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Ошибка сохранения: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Ошибка сохранения игры: {str(e)}'}), 500


@app.route('/saved_games')
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


@app.route('/player/<int:id>')
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
                app.logger.error(f"Partner query error: {str(e)}")
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
        app.logger.error(f"Error in player_stats: {str(e)}", exc_info=True)
        return render_template('500.html'), 500


@app.route('/api/players')
@login_required
def get_players():
    players = Player.query.with_entities(Player.name).all()
    return jsonify([{'name': p.name} for p in players])

@app.route('/api/search_players')
def search_players():
    search_term = request.args.get('term', '')
    players = Player.query.filter(Player.name.ilike(f'%{search_term}%')).limit(10).all()
    return jsonify([player.name for player in players])

@app.template_filter('datetime')
def format_datetime(value):
    moscow_tz = pytz.timezone('Europe/Moscow')
    if value.tzinfo is None:
        value = pytz.utc.localize(value)
    localized = value.astimezone(moscow_tz)
    return localized.strftime('%d.%m.%Y')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)