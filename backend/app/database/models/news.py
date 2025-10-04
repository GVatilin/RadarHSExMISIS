from sqlalchemy import Column, String, Boolean, UUID, func, DateTime, Integer, ForeignKey, Float
from sqlalchemy.orm import validates, relationship
from app.database import DeclarativeBase
import uuid


class Entity(DeclarativeBase):
    __tablename__ = "Entities"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    name = Column(String)
    news_id = Column(UUID, ForeignKey("News.id"), index=True)
    news = relationship("News")


class Source(DeclarativeBase):
    __tablename__ = "Sources"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    name = Column(String)
    news_id = Column(UUID, ForeignKey("News.id"), index=True)
    news = relationship("News")


class Timeline(DeclarativeBase):
    __tablename__ = "Timelines"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )

    channel = Column(String)
    date = Column(DateTime(timezone=True), nullable=False)
    news_id = Column(UUID, ForeignKey("News.id"), index=True)
    news = relationship("News")


class News(DeclarativeBase):
    __tablename__ = "News"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
    )

    headline = Column(String)
    text = Column(String)
    hotness = Column(Float, nullable=True)
    sentiment = Column(Integer, nullable=True)
    why_now = Column(String, nullable=True)

    entities = relationship(
        "Entity",
        back_populates="news",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    
    sources = relationship(
        "Source",
        back_populates="news",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    timeline = relationship(
        "Timeline",
        back_populates="news",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )