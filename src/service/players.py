from flask_sqlalchemy.session import Session
from sqlalchemy.exc import IntegrityError

from src.infra.chache import player_cache, another_cache
from src.infra.models import Player
from src.infra.repositories.players import PlayerRepository
from src.service.dto.errors import PlayerAlreadyExist
from src.service.dto.players import PlayerModelShort
from src.utils.textsearch import search_nicknames


class PlayerService:
    def __init__(self, session: Session):
        self.session = session
        self.players_repository = PlayerRepository(session)

    def get_player(self, **kwargs) -> PlayerModelShort | None:
        cache_key = frozenset(kwargs.items())
        @player_cache.cache_on_arguments()
        def _get(keys: frozenset) -> PlayerModelShort | None:
            print(f"search player {kwargs=}")
            db_player = self.players_repository.get_one_or_none(**dict(keys))
            return PlayerModelShort.from_db(db_player) if db_player else None
        return _get(cache_key)

    def get_players(self, **kwargs) -> list[PlayerModelShort]:
        cache_key = frozenset(kwargs.items())
        @player_cache.cache_on_arguments()
        def _get(keys: frozenset) -> list[PlayerModelShort]:
            print(f"search players {kwargs=}")
            players = self.players_repository.get_few(**dict(keys))
            return [PlayerModelShort.from_db(p) for p in players]
        return _get(cache_key)

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

    def search_players(self, search_sting: str, limit: int = 5) -> list[PlayerModelShort]:
        @player_cache.cache_on_arguments()
        def _build_players_map() -> dict[str, int]:
            all_players: list[PlayerModelShort] = self.get_players()
            return {player.nickname: player.id for player in all_players}
        players_map = _build_players_map()

        results = search_nicknames(search_sting, players_map.keys(), limit)

        return [PlayerModelShort(id=players_map[nickname], nickname=nickname) for nickname in results]


    def update_player(self, **kwargs):
        ...

    def merge_players(self, target_player: Player, source_player: Player) -> Player:
        self.players_repository.remove(source_player)
        self.session.commit()
        return target_player
