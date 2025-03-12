from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.infra.database import db
from src.infra.models import Player

admin_router = Blueprint('admin_router', __name__)

@admin_router.route('/admin/add_gg', methods=['GET', 'POST'])
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
