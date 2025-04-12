from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.infra.database.database import get_session
from src.service.dto.errors import PlayerNotFoundError, NicknameUnavailable, PlayerAlreadyExist
from src.service.dto.players import PlayerModelShort
from src.service.players import PlayerService

players_router = APIRouter(prefix="/players", tags=["players"], redirect_slashes=True)

@players_router.get('', description="Get all players")
def get_players(session: Session = Depends(get_session)) -> list[PlayerModelShort]:
    service = PlayerService(session=session)
    players = service.get_players()
    return players

@players_router.get('/search', description="Get all players")
def search_players(nickname: str, session: Session = Depends(get_session)) -> list[PlayerModelShort]:
    service = PlayerService(session=session)
    players = service.search_players(nickname)
    return players

@players_router.get('/{player_id}', description="Get player by ID")
def get_player(player_id: int, session: Session = Depends(get_session)) -> PlayerModelShort:
    service = PlayerService(session=session)
    player = service.get_player(id=player_id)
    print(player)
    if not player:
        raise PlayerNotFoundError(player_id)
    return player

@players_router.post('', description="Create new player")
def create_player(nickname: str, session: Session = Depends(get_session)) -> PlayerModelShort:
    service = PlayerService(session=session)
    try:
        return service.create_player(nickname)
    except PlayerAlreadyExist:
        raise NicknameUnavailable(nickname)


@players_router.delete('/{player_id}', description="Delete player")
def delete_player(player_id: int):
    ...

def update_player(player_id: int):
    ...
