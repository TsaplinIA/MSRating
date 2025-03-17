from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException

from src.service.dto.errors import UsernameUnavailable
from src.service.dto.users import UserModel, LoginUserRequest, UserModelShort
from src.service.login import login_manager
from src.service.users import UserService

login_router = APIRouter(prefix="/auth", tags=["login"], redirect_slashes=True)


@login_router.post("/login", description="Get access token (JWT)")
def login(
        data: OAuth2PasswordRequestForm = Depends(),
        user_service: UserService = Depends(UserService.get_service),
):
    user: UserModel = user_service.get_user_by_username(data.username)
    if not user:
        raise InvalidCredentialsException
    if not user_service.validate_password(user, data.password):
        raise InvalidCredentialsException

    access_token = login_manager.create_access_token(
        data=dict(sub=data.username)
    )
    return {'access_token': access_token, 'token_type': 'bearer'}

@login_router.post("/register", description="Register new user")
def register(
        data: LoginUserRequest,
        user_service: UserService = Depends(UserService.get_service),
) -> UserModelShort:
    user = user_service.get_user_by_username(data.username)
    if user:
        raise UsernameUnavailable(username=data.username)
    new_user = user_service.create_user(data)
    return new_user

@login_router.get("/protected_test", description="test")
def protected(user=Depends(login_manager)) -> str:
    return f"logined user: {user.username}"