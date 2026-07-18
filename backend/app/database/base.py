"""SQLAlchemy declarative base for all ORM models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class ORM for all ORM Models

    Every ORM moedl (NoteORM, FolderORM etc) inherits from this.
    Base collects table metadata so create_all() can create all tables
    """

    pass
