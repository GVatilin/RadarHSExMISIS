from fastapi import APIRouter, Depends, Security, status, HTTPException, \
    Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID
from app.database.connection import get_session

from app.schemas import AddChannelForm
from app.utils.tg_channel import add_channel_utils


api_router = APIRouter(
    prefix="/channel",
    tags=["Channel"]
)


@api_router.post('/add_channel',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def add_channel(department: Annotated[AddChannelForm, Body()],
                      session: Annotated[AsyncSession, Depends(get_session)]
                      ) -> None:
    is_success = await add_channel_utils(department, session)

    if is_success:
        return {"message": "Channel added!"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, \
                        detail="Error add channel")
