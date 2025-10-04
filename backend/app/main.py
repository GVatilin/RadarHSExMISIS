# main.py
from logging import getLogger
from fastapi import FastAPI
from uvicorn import run
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import DefaultSettings, get_settings
from app.endpoints import list_of_routes
from app.endpoints.admin import flask_app

from app.utils.tg_fetch import poll_all_channels_once, get_pyro_client
import logging, sys

logging.basicConfig(
    level=logging.INFO,  # можно DEBUG для подробностей
    format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logging.getLogger("apscheduler").setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.INFO)   # на время — можно WARNING потом
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logger = getLogger(__name__)


def bindRoutes(application: FastAPI, setting: DefaultSettings) -> None:
    for route in list_of_routes:
        application.include_router(route, prefix=setting.PATH_PREFIX)


def getApp() -> FastAPI:
    description = "Radar HSExMISIS"
    application = FastAPI(
        docs_url="/api/v1/swagger",
        openapi_url="/api/v1/openapi",
        version="1.0.0",
        title="Radar",
        description=description,
    )
    settings = get_settings()
    bindRoutes(application, settings)
    application.state.settings = settings
    return application


app = getApp()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key="your_random_secret_key",
)

app.mount("/panel", WSGIMiddleware(flask_app))


scheduler = AsyncIOScheduler()

async def _poll_job():
    await poll_all_channels_once()

@app.on_event("startup")
async def on_startup():
    await get_pyro_client()
    scheduler.add_job(_poll_job, "interval", minutes=3, id="tg_poll_every_2m",
                      max_instances=1, coalesce=True)
    scheduler.start()


@app.on_event("shutdown")
async def on_shutdown():
    try:
        scheduler.shutdown(wait=False)
    except Exception:
        pass

if __name__ == "__main__":
    settings_for_application = get_settings()
    run(
        "main:app",
        port=settings_for_application.BACKEND_PORT,
        reload=True,
        reload_dirs=["app"],
        log_level="debug",
        host=settings_for_application.BACKEND_HOST,
    )
