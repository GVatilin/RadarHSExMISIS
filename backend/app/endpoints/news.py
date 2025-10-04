from fastapi import APIRouter, Depends, Security, status, HTTPException, \
    Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID
from app.database.connection import get_session

from app.schemas import AddChannelForm, NewsResponse, NewsPostCreate, NewsPostResponse
from app.utils.news import get_all_news_utils, get_report_utils, create_news_utils


api_router = APIRouter(
    prefix="/news",
    tags=["News"]
)


@api_router.get('/get_all_news',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def get_all_news(session: Annotated[AsyncSession, Depends(get_session)]
                       ) -> NewsResponse:
    return await get_all_news_utils(session)


@api_router.get('/get_report',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def get_report(session: Annotated[AsyncSession, Depends(get_session)]
                     ) -> NewsResponse:
    return await get_report_utils(session)


@api_router.post('/create_news',
            status_code=status.HTTP_200_OK,
            responses={
                     status.HTTP_401_UNAUTHORIZED: {
                         "descriprion": "Non authorized"
                     }
                 })
async def create_news(payload: Annotated[NewsPostCreate, Body()],
                      session: Annotated[AsyncSession, Depends(get_session)]
                     ) -> NewsPostResponse:
    return await create_news_utils(payload, session)

