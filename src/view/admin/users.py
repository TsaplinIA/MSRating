from starlette_admin.contrib.sqla import ModelView

from src.infra.models import User


class PlayerView(ModelView):
    fields = [
        "id",
        "username",
        "is_admin",
    ]
    fields_default_sort = ["username"]
    exclude_fields_from_list = [
        "id",
    ]
    exclude_fields_from_create = ["id"]
    exclude_fields_from_edit = ["id"]

    sortable_fields = ["username"]
    searchable_fields = ["username"]


users_admin_view = PlayerView(User, label="Users")
