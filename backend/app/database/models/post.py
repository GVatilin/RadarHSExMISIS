from sqlalchemy import Column, String, Boolean, UUID, func, DateTime, Integer, ForeignKey

from app.database import DeclarativeBase
import uuid


class Post(DeclarativeBase):
    __tablename__ = "Posts"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )

    text = Column(String)
    date = Column(DateTime)