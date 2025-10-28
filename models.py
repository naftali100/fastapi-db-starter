from sqlmodel import Field, Session, SQLModel, create_engine, select, Column, TIMESTAMP
from sqlalchemy.sql import func


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(default=None, max_length=255)
    email: str = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    created_at: str = Field(default=func.now(), max_length=255)


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None
