from pathlib import Path

from fastapi import Request
from fastapi.responses import FileResponse

from src import config
from src.view.pages.base import pages_router, templates


@pages_router.get("/new_game")
async def get_new_game():
    file_path = config.STATIC_DIR / "new_game" / "index.html"
    return FileResponse(file_path, media_type="text/html")
