from pydantic import BaseModel, Field

from src.infra.models import User as DBUser


class UserModel(BaseModel):
    username: str
    password_hash: str | bytes
    is_admin: bool

    @staticmethod
    def from_db(user: DBUser):
        return UserModel(username=user.username, password_hash=user.password_hash, is_admin=user.is_admin)

class UserModelShort(BaseModel):
    username: str
    is_admin: bool

class LoginUserRequest(BaseModel):
    username: str = Field(..., example='Bodren')
    password: str = Field(..., example='<PASSWORD>')