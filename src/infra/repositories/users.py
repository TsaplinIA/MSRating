from sqlalchemy.orm import Session

from src.infra.models import User
from src.infra.repositories.base import BaseDBRepository


class UserRepository(BaseDBRepository[User]):
    def __init__(self, session: Session):
        super().__init__(session, User)
