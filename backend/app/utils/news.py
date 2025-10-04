from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import News, Source, Timeline, Entity
from app.schemas import NewsResponse, NewsPostResponse, TimelineResponse, NewsPostCreate


def _tz_aware(dt):
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

async def get_all_news_utils(session) -> NewsResponse:
    stmt = (
        select(News)
        .options(
            selectinload(News.entities),
            selectinload(News.sources),
            selectinload(News.timeline),
        )
    )
    res = await session.execute(stmt)
    items: List[News] = res.scalars().unique().all()

    posts: List[NewsPostResponse] = []
    for n in items:
        entities: Optional[List[str]] = [e.name for e in (n.entities or [])] or None
        sources:  Optional[List[str]] = [s.name for s in (n.sources  or [])] or None
        timeline: Optional[List[TimelineResponse]] = (
            [TimelineResponse(channel=t.channel, date=_tz_aware(t.date)) for t in (n.timeline or [])] or None
        )

        posts.append(
            NewsPostResponse(
                headline = n.headline,
                text     = n.text,
                hotness  = float(n.hotness) if n.hotness is not None else 0.0,
                sentiment= int(n.sentiment) if n.sentiment is not None else 0,
                why_now  = n.why_now,
                entities = entities,
                sources  = sources,
                timeline = timeline,
            )
        )

    return NewsResponse(news=posts)


async def get_report_utils(session: AsyncSession) -> NewsResponse:
    pass


async def create_news_utils(payload: NewsPostCreate, session: AsyncSession) -> NewsPostResponse:
    news = News(
        headline = payload.headline or "",
        text     = payload.text or "",
        hotness  = payload.hotness,
        sentiment= payload.sentiment,
        why_now  = payload.why_now,
    )
    session.add(news)
    await session.flush()

    if payload.entities:
        session.add_all([Entity(name=name, news_id=news.id) for name in payload.entities])

    if payload.sources:
        session.add_all([Source(name=name, news_id=news.id) for name in payload.sources])

    if payload.timeline:
        session.add_all([
            Timeline(channel=t.channel, date=_tz_aware(t.date), news_id=news.id)
            for t in payload.timeline
        ])

    await session.commit()
    await session.refresh(news)

    return NewsPostResponse(
        headline = news.headline or "",
        text     = news.text or "",
        hotness  = float(news.hotness) if news.hotness is not None else 0.0,
        sentiment= int(news.sentiment) if news.sentiment is not None else 0,
        why_now  = news.why_now,
        entities = payload.entities or None,
        sources  = payload.sources or None,
        timeline = payload.timeline or None,
    )