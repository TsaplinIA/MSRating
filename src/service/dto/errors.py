from fastapi import HTTPException


class BaseError(HTTPException):
    ...

class PlayerNotFoundError(BaseError):
    def __init__(self, player_id: int):
        msg = f"Player with id={player_id} not found"
        super().__init__(status_code=404, detail=msg)

class UsernameUnavailable(BaseError):
    def __init__(self, username: str):
        msg = f"Sorry, this username({username}) is not available"
        super().__init__(status_code=400, detail=msg)
