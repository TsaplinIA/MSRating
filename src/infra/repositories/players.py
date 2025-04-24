from sqlalchemy.orm import Session

from src.infra.models import Player
from src.infra.repositories.base import BaseDBRepository


class PlayerRepository(BaseDBRepository[Player]):
    def __init__(self, session: Session):
        super().__init__(session, Player)

