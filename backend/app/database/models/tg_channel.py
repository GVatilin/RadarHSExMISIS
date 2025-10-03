from sqlalchemy import Column, String, Boolean, UUID, func, DateTime, Integer

from app.database import DeclarativeBase
import uuid


class Channel(DeclarativeBase):
    __tablename__ = "Channels"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )

    username = Column(String, nullable=False)
    last_message_num = Column(Integer)