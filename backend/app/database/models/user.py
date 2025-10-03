from sqlalchemy import Column, String, Boolean, UUID, func, DateTime, Integer

from app.database import DeclarativeBase
import uuid


class User(DeclarativeBase):
    __tablename__ = "Users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )
    username = Column(String, index=True, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
