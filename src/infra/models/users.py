import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.database.database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(sa.String(72), nullable=False)
    is_admin: Mapped[bool] = mapped_column(sa.Boolean, default=False)
