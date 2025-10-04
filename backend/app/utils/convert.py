# app/utils/report_pipeline.py

from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Post, Channel, News, Entity, Source, Timeline
from app.schemas import NewsPostResponse
from app.utils.convert_agent import get_aggregated_news  

def _utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

async def _load_last_hour_items(session: AsyncSession) -> List[Dict[str, Any]]:
    since = datetime.now(timezone.utc) - timedelta(hours=15)
    res = await session.execute(
        select(Post).where(Post.date >= since).order_by(Post.date.desc())
    )
    posts: List[Post] = res.scalars().all()
    if not posts:
        return []

    # channel_id -> username
    chan_ids = {p.channel_id for p in posts if p.channel_id}
    chan_map: Dict[str, str] = {}
    if chan_ids:
        rows = await session.execute(
            select(Channel.id, Channel.username).where(Channel.id.in_(chan_ids))
        )
        chan_map = {str(cid): uname for cid, uname in rows.all()}

    # готовим для промпта
    items: List[Dict[str, Any]] = []
    for p in posts:
        username = chan_map.get(str(p.channel_id), "")
        items.append({
            "text": p.text or "",
            "date": _utc(p.date).isoformat() if p.date else None,
            "channel": username,
            "message_num": getattr(p, "message_num", None),
        })
    return items

async def _load_existing_headlines(session: AsyncSession, days: int = 7) -> List[str]:
    """Заголовки уже сохранённых новостей за последние `days` (чтобы промпт не раздувался)."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = await session.execute(
        select(News.headline)
    )

    return [h for (h,) in rows.all() if h]

async def convert(session: AsyncSession) -> int:
    items = await _load_last_hour_items(session)
    if not items:
        return 0

    # 1) заголовки, которых надо избежать (последние 7 дней)
    existing_heads_list = await _load_existing_headlines(session, days=7)

    # 2) вызов LLM с «исключениями»
    raw = await get_aggregated_news(items, exclude_headlines=existing_heads_list)
    raw_items = raw["news"] if isinstance(raw, dict) and "news" in raw else raw or []

    rows_src = await session.execute(select(Source.name))
    existing_links: Set[str] = {r[0] for r in rows_src.all() if r[0]}
    rows_heads = await session.execute(select(News.headline))
    existing_heads: Set[str] = {(h or "").strip().lower() for (h,) in rows_heads.all()}

    created = 0
    for obj in raw_items:
        story = NewsPostResponse.model_validate(obj)

        if any(s in existing_links for s in (story.sources or [])):
            continue
        if (story.headline or "").strip().lower() in existing_heads:
            continue

        # сохранить
        news = News(
            headline=story.headline,
            text=story.text,
            hotness=story.hotness,
            sentiment=story.sentiment,
            why_now=story.why_now,
        )
        session.add(news)
        await session.flush()

        for name in (story.entities or []):
            session.add(Entity(name=name, news_id=news.id))
        for url in (story.sources or []):
            session.add(Source(name=url, news_id=news.id))
        for t in (story.timeline or []):
            session.add(Timeline(channel=t.channel, date=t.date, news_id=news.id))

        created += 1
        existing_heads.add((story.headline or "").strip().lower())
        for s in (story.sources or []):
            existing_links.add(s)

    return created
