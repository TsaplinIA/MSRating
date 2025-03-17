from passlib.context import CryptContext

# Создаем контекст хеширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля его хешу."""
    return pwd_context.verify(plain_password, hashed_password)
