from sqlalchemy import Column, String, Boolean, UUID, func, DateTime, Integer, ForeignKey

from app.database import DeclarativeBase
import uuid


class News(DeclarativeBase):
    __tablename__ = "News"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )

    description = Column(String)
    text = Column(String)