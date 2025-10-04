# app/services/tg_poll_pyro_async.py
import os
import asyncio
from datetime import timezone
from typing import Optional, List
from fastapi import HTTPException
from pyrogram import Client
from pyrogram.errors import FloodWait
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_session
from app.database.models import Channel, Post
from app.config import get_settings
from app.database.connection.session import async_session_maker
from app.utils.convert import convert 

_pyro: Optional[Client] = None

def _build_pyro() -> Client:
    s = get_settings()
    api_id = int(s.TG_API_ID)
    api_hash = s.TG_API_HASH
    session_string = s.TG_SESSION_STRING

    return Client(":memory:", api_id=api_id, api_hash=api_hash, session_string=session_string)

async def get_pyro_client() -> Client:
    global _pyro
    if _pyro:
        return _pyro
    _pyro = _build_pyro()
    await _pyro.start()
    return _pyro

# ----------- utils -----------
def _to_utc(dt):
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

from logging import getLogger
log = getLogger("radar")

async def poll_channel_once(db: AsyncSession, ch: Channel) -> int:
    app = await get_pyro_client()

    username = ch.username.lstrip("@")
    since_id = ch.last_message_num or 0

    max_seen = since_id
    cnt = 0
    page_size = 10

    log.info("poll %s since_id=%s", username, since_id)

    async for m in app.get_chat_history(username, offset_id=0, limit=page_size):
        if m.id <= since_id:
            continue
        text = (m.text or m.caption or "").strip()
        if not text or not m.date:
            continue
        log.info(f"Пост {text}")
        post = (
            Post(
                text=text,
                date=_to_utc(m.date),
                channel_id=ch.id,
                message_num=m.id,
            )
        )
        if m.id > max_seen:
            max_seen = m.id
        
        db.add(post)
        cnt += 1

    if cnt:
        await db.execute(
            update(Channel)
            .where(Channel.id == ch.id)
            .values(last_message_num=max_seen)
        )

        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return 0


async def poll_all_channels_once() -> int:
    total = 0
    async with async_session_maker() as session:
        res = await session.execute(select(Channel))
        channels = res.scalars().all()
        for ch in channels:
            try:
                log.info("start channel")
                added = await poll_channel_once(session, ch)
                total += added
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                log.exception("poll_channel_once failed")
                continue

        await session.commit()

        try:
            created = await convert(session)
            log.info("aggregated news stored: %s", created)
            await session.commit()
        except Exception:
            log.exception("failed to aggregate/store news")
            await session.rollback()

    return total