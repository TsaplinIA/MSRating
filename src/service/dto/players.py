from pydantic import BaseModel, Field

from src.infra.models import Player as DBPlayer


class PlayerModelShort(BaseModel):
    id: int = Field(..., example="777")
    nickname: str = Field(..., example="Bodren")

    @staticmethod
    def from_db(player: DBPlayer):
        return PlayerModelShort(id=player.id, nickname=player.nickname)
