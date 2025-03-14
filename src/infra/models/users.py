from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.database import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)
    is_admin: Mapped[bool] = mapped_column(db.Boolean, default=False)
