from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select

from app.config import DefaultSettings, get_settings
from app.database.connection import get_session
from app.database.models import Channel


async def add_channel_utils(payload, session) -> None:
    channel = Channel(username=payload.username, last_message_num=0)
    session.add(channel)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return True