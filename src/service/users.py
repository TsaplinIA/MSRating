from fastapi import Depends
from sqlalchemy.orm import Session

from src.infra.database.database import get_session
from src.infra.models import User
from src.infra.repositories.users import UserRepository
from src.service.dto.users import LoginUserRequest, UserModel, UserModelShort
from src.utils.hash import hash_password, verify_password


class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.players_repository = UserRepository(session)

    def get_user_by_username(self, username: str) -> UserModel | None:
        db_user = self.players_repository.get_one_or_none(username=username)
        return UserModel.from_db(db_user) if db_user else None

    @staticmethod
    def validate_password(user: UserModel, password: str) -> bool:
        return verify_password(password, user.password_hash)

    def create_user(self, body: LoginUserRequest) -> UserModelShort:
        hashed_password = hash_password(body.password)
        self.session.add(User(username=body.username, password_hash=hashed_password))
        self.session.commit()
        return UserModelShort(username=body.username, is_admin=False)

    @staticmethod
    def get_service(session: Session = Depends(get_session)) -> 'UserService':
        return UserService(session)
