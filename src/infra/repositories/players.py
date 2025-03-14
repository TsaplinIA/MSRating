from src.infra.models import PlayerModel
from src.infra.repositories.base import BaseDBRepository


class PlayerRepository(BaseDBRepository[PlayerModel]):
    def __init__(self, session):
        super().__init__(session, PlayerModel)

