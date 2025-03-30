from flask_sqlalchemy.session import Session
from sqlalchemy.exc import IntegrityError

from src.infra.models import Player
from src.infra.repositories.players import PlayerRepository
from src.service.dto.errors import PlayerAlreadyExist
from src.service.dto.players import PlayerModelShort


class PlayerService:
    def __init__(self, session: Session):
        self.session = session
        self.players_repository = PlayerRepository(session)

    def get_player(self, **kwargs) -> PlayerModelShort | None:
        db_player = self.players_repository.get_one_or_none(**kwargs)
        return PlayerModelShort.from_db(db_player) if db_player else None

    def get_players(self, **kwargs) -> list[PlayerModelShort]:
        players = self.players_repository.get_few(**kwargs)
        return [PlayerModelShort.from_db(p) for p in players]

    def create_player(self, nickname: str) -> PlayerModelShort:
        if self.get_player(nickname=nickname) is not None:
            raise PlayerAlreadyExist(nickname)
        player = Player(nickname=nickname)
        try:
            self.players_repository.create(player)
            self.session.commit()
            return PlayerModelShort.from_db(player)
        except IntegrityError:
            self.session.rollback()
            raise PlayerAlreadyExist(nickname)

    def update_player(self, **kwargs):
        ...

    def merge_players(self, target_player: Player, source_player: Player) -> Player:
        self.players_repository.remove(source_player)
        self.session.commit()
        return target_player
