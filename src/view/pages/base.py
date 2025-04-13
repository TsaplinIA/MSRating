from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from src import config

pages_router = APIRouter(redirect_slashes=True)
templates = Jinja2Templates(directory=config.TEMPLATE_DIR)