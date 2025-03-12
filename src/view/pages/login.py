from flask import request, flash, redirect, url_for, render_template, Blueprint
from flask_login import login_required, logout_user, LoginManager, login_user

from src.infra.database import db
from src import config
from src.infra.models import User

login_router = Blueprint('login', __name__)
login_manager = LoginManager()
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_router.route('/login', methods=['GET', 'POST'])
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

@login_router.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin_code = request.form.get('admin_code', '').strip()

        is_admin = (admin_code == config.ADMIN_SECRET_CODE)

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

@login_router.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))