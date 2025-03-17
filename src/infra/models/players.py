from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa

from src.infra.database.database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    nickname: Mapped[str] = mapped_column(sa.String(100), unique=True, nullable=False)
