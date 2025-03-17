from src.infra.database.database import Session
from src.infra.login_manager import manager, AuthenticatedUserNotFoundException
from src.service.users import UserService

auth_session = Session()
auth_user_service = UserService(auth_session)

@manager.user_loader()
def load_user(username: str):
    user = auth_user_service.get_user_by_username(username)
    if not user:
        raise AuthenticatedUserNotFoundException(username)
    return user

login_manager = manager