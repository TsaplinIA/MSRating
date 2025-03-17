from starlette_admin.contrib.sqla import Admin as SQLAAdmin

from src.infra.database.database import engine
from src.view.admin.users import users_admin_view


class Admin(SQLAAdmin):
    pass

def init_admin(engine, title="MSRating AdminPanel"):
    admin = Admin(
        engine,
        title=title,
    )

    admin.add_view(users_admin_view)
    return admin

admin = init_admin(engine)

__all__ = ["admin"]
