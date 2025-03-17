from contextlib import asynccontextmanager
import pytz
import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from src import config
from src.infra.database.database import Base, engine
from src.infra.logging_config import init_logging_config
from src.view.api.login import login_router

from src.view.api.players import players_router



def format_datetime(value):
    moscow_tz = pytz.timezone('Europe/Moscow')
    if value.tzinfo is None:
        value = pytz.utc.localize(value)
    localized = value.astimezone(moscow_tz)
    return localized.strftime('%d.%m.%Y')



@asynccontextmanager
async def lifespan(app: FastAPI, *args, **kwargs):
    Base.metadata.create_all(engine)
    yield



def init_fastapi_app():

    app = FastAPI(lifespan=lifespan, title="MSRating", summary="API for manage MafiaStyle rating", version="0.2.1")
    init_logging_config()

    app.mount("/static", StaticFiles(directory=config.STATIC_DIR.resolve()), name="static")
    app.include_router(players_router, prefix="/api")
    app.include_router(login_router, prefix="/api")
    return app


fastapi_app = init_fastapi_app()

if __name__ == "__main__":
    uvicorn.run("src.app:fastapi_app", host=config.HOST, port=config.PORT)