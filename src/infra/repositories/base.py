import logging
from typing import Self

from flask_sqlalchemy.session import Session
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class BaseDBRepository[T]:
    def __init__(self, session: Session, model: type[T]):
        self.session = session
        self.model = model  # Теперь можно передавать модель напрямую

    def get_one_or_none(self, **kwargs) -> T | None:
        """Получает объект"""
        try:
            return self.session.query(self.model).filter_by(**kwargs).one_or_none()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while fetching {self.model.__name__}: {e}")

    def get_few(self, **kwargs) -> list[T]:
        try:
            return self.session.query(self.model).filter_by(**kwargs).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while fetching {self.model.__name__}: {e}")

    def remove(self, obj: T) -> Self:
        """Удаляет объект из БД и возвращает self для чейнинга."""
        if not isinstance(obj, self.model):
            raise TypeError(f"Expected an instance of {self.model.__name__}")
        self.session.delete(obj)
        return self

    def create(self, obj: T) -> Self:
        if not isinstance(obj, self.model):
            raise TypeError(f"Expected an instance of {self.model.__name__}")
        self.session.add(obj)
        return self