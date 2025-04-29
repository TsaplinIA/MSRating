from sqlalchemy.orm import Session

from src.infra.models import Game, GameResult
from src.infra.repositories.base import BaseDBRepository


class GameRepository(BaseDBRepository[Game]):
    def __init__(self, session: Session):
        super().__init__(session, Game)


class GameResultRepository(BaseDBRepository[GameResult]):
    def __init__(self, session: Session):
        super().__init__(session, GameResult)