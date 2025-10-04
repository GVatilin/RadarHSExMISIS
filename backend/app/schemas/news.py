from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List
from datetime import datetime


class TimelineResponse(BaseModel):
    channel: str
    date: datetime


class NewsPostResponse(BaseModel):
    headline: str
    text: str
    hotness: float
    sentiment: int
    why_now: Optional[str]
    entities: Optional[List[str]]
    sources: Optional[List[str]]
    timeline: Optional[List[TimelineResponse]]


class NewsResponse(BaseModel):
    news: List[NewsPostResponse]


class NewsPostCreate(BaseModel):
    headline: Optional[str]
    text: Optional[str]
    hotness: Optional[float]
    sentiment: Optional[int]
    why_now: Optional[str]
    entities: Optional[List[str]]
    sources: Optional[List[str]]
    timeline: Optional[List[TimelineResponse]]