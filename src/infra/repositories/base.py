from typing import Self

from flask_sqlalchemy.session import Session
from sqlalchemy.exc import SQLAlchemyError


class BaseDBRepository[T]:
    def __init__(self, session: Session, model: type[T]):
        self.session = session
        self.model = model  # Теперь можно передавать модель напрямую

    def get(self, **kwargs) -> T | None:
        """Получает объект"""
        try:
            return self.session.query(self.model).filter_by(**kwargs).one_or_none()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error while fetching {self.model.__name__}: {e}")

    def save(self, obj: T) -> Self:
        """Сохраняет изменения в объекте и возвращает self для чейнинга."""
        if not isinstance(obj, self.model):
            raise TypeError(f"Expected an instance of {self.model.__name__}")
        try:
            self.session.commit()
            return self
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Database error while saving {self.model.__name__}: {e}")

    def remove(self, obj: T) -> Self:
        """Удаляет объект из БД и возвращает self для чейнинга."""
        if not isinstance(obj, self.model):
            raise TypeError(f"Expected an instance of {self.model.__name__}")
        try:
            self.session.delete(obj)
            self.session.commit()
            return self
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Database error while removing {self.model.__name__}: {e}")