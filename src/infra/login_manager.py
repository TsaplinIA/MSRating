from datetime import timedelta

from fastapi import HTTPException
from fastapi_login import LoginManager

from src import config

class NotAuthenticatedException(HTTPException):
    def __init__(self):
        msg = f"Not Authenticated!"
        super().__init__(status_code=401, detail=msg)

class AuthenticatedUserNotFoundException(HTTPException):
    def __init__(self, username: str):
        msg = f"Authenticated user({username}) not found!"
        super().__init__(status_code=403, detail=msg)

manager = LoginManager(
    secret=config.APP_SECRET_KEY,
    token_url='/api/auth/login',
    default_expiry = timedelta(days=7),
    not_authenticated_exception=NotAuthenticatedException
)
