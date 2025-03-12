from flask import Blueprint, render_template, session
from flask_login import current_user, login_required

new_router = Blueprint('new_router', __name__)

@new_router.route('/new')
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
